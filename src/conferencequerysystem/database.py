import sqlite3
import json
import pandas as pd
import threading
import queue
from conferencequerysystem.consts import (GetBoothNameTable,
                                          GetDataBasePath,
                                          GetUsrIdentiryColumnNames,
                                          GetUnstructuredDataSaveDir
                                          )
from PIL import Image
import os
from enum import Enum
from io import BytesIO
from pathlib import Path

class EFileSubmissionSaveType(Enum):
    NoType = 1
    Photo = 2
    Video = 3

class FileSubmission:
    def __init__(self, fileSaveType=EFileSubmissionSaveType.NoType, buffer=None, savePath=None):
        self.fileType = fileSaveType
        self.buffer = buffer
        self.savePath = savePath


class UnstructuredDataSaveUtility:
    def __init__(self, saveRootDir = GetUnstructuredDataSaveDir()):
        self.saveRootDir = saveRootDir
        self.fileNameUserInfoJoinCharacter = "_"

    def ComposeSavePathForUser(self, userInfos, boothName, ext):
        fileName = f"{self.ComposeSaveFileNameForUser(userInfos)}{ext}"
        return os.path.normpath(os.path.join(self.GetSaveDirForCategory(boothName), fileName))

    def GetSaveDirForCategory(self, category):
        saveDir = os.path.normpath(os.path.join(self.saveRootDir, category))
        if not os.path.exists(saveDir):
            os.makedirs(saveDir, exist_ok=True)

        return saveDir

    def ComposeSaveFileNameForUser(self, userInfos):
         return f"{self.fileNameUserInfoJoinCharacter.join(userInfos)}"

    def SaveSubmission(self, fileSubmission: FileSubmission):
        if fileSubmission.fileType == EFileSubmissionSaveType.NoType:
            return

        tmp_path = fileSubmission.savePath + ".part"
        with open(tmp_path, "wb") as f:
            f.write(fileSubmission.buffer)

            # f.flush() push the data in the file out of the executable's memory, so it should just live in the os's memory
            # f.fileno() returns the file number of the file, a unique id(or called descriptor) that is used in the underlying operating system to locate the file
            # os.sfync(fileId) means write the file data from memory to disk right now, this ensures it is saved even the program crashes
            # so f.flush() make sure that the memory is now in the hand of the os, and os.fsync(f.fileno()) ensures the file is on disk.
            f.flush()
            os.fsync(f.fileno())

        os.replace(tmp_path, fileSubmission.savePath)

    def SubmissionFilePathToUserInfo(self, filePath):
        stem = Path(filePath).stem
        userInfos = stem.split(self.fileNameUserInfoJoinCharacter)
        return f"{userInfos[2]} {userInfos[0]} from {userInfos[1]}"


class UserUpdateInfo:
    """
    ***arguments:*** 
    * info(list(str)): user name, and all other infomations like (school, occupation, from, etc), used to find a user or add a user
    * boothName(str): the booth the user has visited
    * fileSubmission(FileSubmission): the file the user has uploaded, currently supports image only.
    """
    def __init__(self, userInfos, boothName, fileSubmission:FileSubmission):
        self.userInfos = userInfos
        self.boothName = boothName
        self.fileSubmission: FileSubmission = fileSubmission

    def __str__(self):
        basicInfo = " ".join(self.userInfos)
        return f"{basicInfo}\nBooth: {self.boothName}\nFile:{self.fileSubmission.fileType.name} at {self.fileSubmission.savePath}"


class DataBase:
    def __init__(self):
        self.dataBasePath = GetDataBasePath()
        # self.connection = sqlite3.connect(dataBasePath, check_same_thread=False)
        # self.cursor = self.connection.cursor()
        self.dtName=  "record"
        self.boothNameTable = GetBoothNameTable()
        self.finishedColumnName = "Finished"
        self.attendedAllColumName = "AttenedAll"

        self.writeQueue = queue.Queue()
        self.threadLock = threading.Lock()
        self.queueThread = None

        self.CreateDataTable()

        with sqlite3.connect(self.dataBasePath) as conn: 
            conn.execute('PRAGMA journal_mode=WAL;')
            conn.commit()

        self.unstructuredSaver = UnstructuredDataSaveUtility()

    def _execute_query(self, query, params=(), commit=False):
        with sqlite3.connect(self.dataBasePath, timeout = 10.0) as connection:
            cursor = connection.cursor()
            cursor.execute(query, params)
            if commit:
                connection.commit()

            return cursor.fetchall()

    def _get_connection_for_pandas(self):
        return sqlite3.connect(self.dataBasePath, timeout=5.0)

    def SubmissionFilePathToUserInfo(self, filePath):
        return self.unstructuredSaver.SubmissionFilePathToUserInfo(filePath)

    def EnqueUserUpdateBoothOnlyNoFileSubmission(self, userInfos, boothName):
        self.EnqueUserUpdate(UserUpdateInfo(userInfos=userInfos, boothName=boothName, fileSubmission=FileSubmission()))

    def EnqueUserUpdate(self, userUpdateInfo: UserUpdateInfo):
        """
        ## Called by front end to update or add a user
        
        ***arguments:***
        - ***userUpdateInfo***(UserUpdateInfo): the user update info that contains user name and others, the booth name, and file submissions if any are present
        ***return:***

        None
        """

        self.writeQueue.put(userUpdateInfo)
        self.StartWriteThread()

    def StartWriteThread(self):
        with self.threadLock:
            if self.queueThread is None or not self.queueThread.is_alive():
                self.queueThread = threading.Thread(target = self.ProcessQueue, daemon=True) 
                print("stating write thread!")
                self.queueThread.start()
        
    def ProcessQueue(self):
        # This thread is the *only* one that will perform commits, ensuring serial write access 
        while not self.writeQueue.empty():
            userUpdateInfo: UserUpdateInfo = self.writeQueue.get()
            # print(f"process queued data:\n{userUpdateInfo}")
            try:
                with sqlite3.connect(self.dataBasePath, timeout = 10.0) as connection:
                    cursor = connection.cursor()
                    self.AddOrUpdateUser(userUpdateInfo, connection, cursor)
                    connection.commit()

                self.unstructuredSaver.SaveSubmission(userUpdateInfo.fileSubmission)
            except sqlite3.OperationalError as e:
                print("=======================EORROR========================")
                print(f"error during write operation: {e}")
                print("=====================================================")
            except Exception as e:
                print("=======================CRITICAL ERROR========================")
                print(f"A non-SQLite error occured: {e}")
                print("=====================================================")
            finally:
                self.writeQueue.task_done()


    def AddOrUpdateUser(self, userUpdateInfo: UserUpdateInfo, connection, cursor):
        record = self.GetRecord(userUpdateInfo.userInfos, connection, cursor)
        if record:
            self.UpdateUser(userUpdateInfo, connection, cursor)
        else:
            self.AddUser(userUpdateInfo, connection, cursor)

    def AddUser(self, userUpdateInfo: UserUpdateInfo, connection, cursor):
        identityColNames = GetUsrIdentiryColumnNames() 
        boothVisitedRecord = []

        boothNames = list(self.boothNameTable.values())
        for boothName in boothNames: 
            identityColNames.append(boothName)
            if boothName == userUpdateInfo.boothName:
                boothVisitedRecord.append('1')
            else:
                boothVisitedRecord.append('0')

        infoColValuesPlaceHolders = ""
        for i in range(len(GetUsrIdentiryColumnNames())):
            infoColValuesPlaceHolders += "?,"

        query = f'INSERT INTO {self.dtName} ({",".join(identityColNames)}) VALUES ({infoColValuesPlaceHolders} {",".join(boothVisitedRecord)})'
        cursor.execute(query,tuple(userUpdateInfo.userInfos))

        self.UpdateUserCompetitionEntry(userUpdateInfo, connection, cursor)


    def UpdateUser(self, userUpdateInfo: UserUpdateInfo, connection, cursor):
        queryFilters = self.ComposeUserQueryFilters()
        boothUpdateQuery = f'UPDATE {self.dtName} Set {userUpdateInfo.boothName} = 1 WHERE {queryFilters}'
        cursor.execute(boothUpdateQuery, tuple(userUpdateInfo.userInfos))

        self.UpdateUserCompetitionEntry(userUpdateInfo, connection, cursor)

    def UpdateUserCompetitionEntry(self, userUpdateInfo: UserUpdateInfo, connection, cursor):
        """
        competition entires are stored as strings with each entry seperated by a comma:
        "entryOne,entryTwo"
        """

        if userUpdateInfo.fileSubmission.fileType == EFileSubmissionSaveType.NoType:
            return

        currentCompetitionEntriesStr = self.GetRecord(userUpdateInfo.userInfos, connection, cursor, self.GetCompetitionColumnName())[0]
        # print(f"{userUpdateInfo.userInfos[0]} currently has: {currentCompetitionEntriesStr} competition entires")
    
        newCompetitionEntry = userUpdateInfo.fileSubmission.savePath
        if currentCompetitionEntriesStr is not None and newCompetitionEntry in currentCompetitionEntriesStr:
            # print(f"{newCompetitionEntry} is already in existing entiries: {currentCompetitionEntriesStr}")
            return

        #compose new competition entries as a str
        newCompetitionEntriesStr = newCompetitionEntry
        if currentCompetitionEntriesStr is not None:
            newCompetitionEntriesStr = f"{newCompetitionEntriesStr},{currentCompetitionEntriesStr}"

        # apply the change to the data base
        queryFilters = self.ComposeUserQueryFilters()
        competitionEntiresUpdateQuery = f'UPDATE {self.dtName} Set {self.GetCompetitionColumnName()} = ? WHERE {queryFilters}'
        competitionEntiresQueryParms = [newCompetitionEntriesStr] + userUpdateInfo.userInfos
        cursor.execute(competitionEntiresUpdateQuery, tuple(competitionEntiresQueryParms))


    def CreateDataTable(self):
        columnDefination = f'''id INTEGER PRIMARY KEY AUTOINCREMENT'''

        for col in GetUsrIdentiryColumnNames():
            columnDefination += f",\n{col} TEXT"

        for boothName in self.GetBoothNames():
            columnDefination += f",\n{boothName} INTEGER"

        columnDefination += f", \n{self.GetCompetitionColumnName()} TEXT"

        self._execute_query(f'CREATE TABLE IF NOT EXISTS {self.dtName} ({columnDefination})', commit=True)


    def GetRecord(self, userInfos, connection = None, cursor = None, recordColumNames="*"):
        query = self.BuildUserQuery(recordColumNames)
        
        if connection and cursor:
            # Internal call (from within a transaction in ProcessQueue)
            cursor.execute(query, tuple(userInfos))
            return cursor.fetchone()
        else:
            # External call (from a separate thread/API endpoint)
            results = self._execute_query(query, tuple(userInfos))
            return results[0] if results else None


    def GetUserRecordAsDataFrame(self, info):
        query = self.BuildUserQuery() 
        with self._get_connection_for_pandas() as conn:
            return pd.read_sql_query(query, conn, params=tuple(info))


    def GetDataAsDataFrame(self):
        query = f"SELECT * FROM {self.dtName}"
        df = None
        with self._get_connection_for_pandas() as conn:
            df = pd.read_sql_query(query, conn)

        # print(df) 
        BoothNames = self.GetBoothNames() 
        df[self.finishedColumnName] = 0
        for boothName in BoothNames:
            df[self.finishedColumnName] += df[boothName]

        df[self.attendedAllColumName] = (df[self.finishedColumnName] == len(BoothNames)).astype(int)
        return df


    def GetCompetitionColumnName(self):
        return "competitions"

    def GetInvalidInfos(self, info):
        InvalidInfo = []
        for i, inf in enumerate(info):
            if inf == "":
                InvalidInfo.append(i)

        return InvalidInfo


    def BuildUserQuery(self, querycolumnName = "*"):
        queryFilters = self.ComposeUserQueryFilters()
        query = f'SELECT {querycolumnName} FROM {self.dtName} WHERE {queryFilters}'
        return query


    def GetUserJourney(self, info):
        df = self.GetUserRecordAsDataFrame(info)
        visited = []
        notVisited = self.GetBoothNames()
        if df.empty:
            return visited, notVisited

        for boothName in self.GetBoothNames():
            if df[boothName].values[0] == 1:
                visited.append(boothName) 
                notVisited.remove(boothName)
        return visited, notVisited

    def HasUser(self, info):
        if self.GetRecord(info):
            return True

        return False

    def GetBoothNames(self):
        return list(self.boothNameTable.values())

    def ComposeUserQueryFilters(self):
        queryFilterList = []
        for col in GetUsrIdentiryColumnNames():
            queryFilterList.append(f"{col}=?")

        return ' AND '.join(queryFilterList)


    def SaveSubmissionForUser(self, userInfos: list[str], boothName: str, fileBuffer, extention):
        savePath = self.unstructuredSaver.ComposeSavePathForUser(userInfos, boothName, extention)
        submissionInfo = FileSubmission(fileSaveType = EFileSubmissionSaveType.Video, buffer = fileBuffer, savePath = savePath)
        self.EnqueUserUpdate(UserUpdateInfo(userInfos, boothName, submissionInfo))

        return True, ""

    def GetUserPrevSubmission(self, userInfos, boothName: str):
        saveDir = self.unstructuredSaver.GetSaveDirForCategory(boothName)
        fileName = self.unstructuredSaver.ComposeSaveFileNameForUser(userInfos)
        for file in os.listdir(saveDir):
            if fileName in file:
                return os.path.normpath(os.path.join(saveDir, file))

        return None
            

