import sqlite3
import json
import pandas as pd
import threading
import queue
from conferencequerysystem.consts import GetBoothNameTable, GetDataBasePath, GetUsrIdentiryColumnNames, GetUnstructuredDataSaveDir
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
        fileName = f"{self.fileNameUserInfoJoinCharacter.join(userInfos)}.{ext}"
        return os.path.normpath(os.path.join(self.GetSaveDirForCategory(boothName), fileName))

    def GetSaveDirForCategory(self, category):
        saveDir = os.path.normpath(os.path.join(self.saveRootDir, category))
        if not os.path.exists(saveDir):
            os.makedirs(saveDir, exist_ok=True)

        return saveDir

    def SaveImage(self, savePath):
        print(f"saving path is: {savePath}")

    def SaveSubmission(self, fileSubmission: FileSubmission):
        tmp_path = fileSubmission.savePath + ".part"
        with open(tmp_path, "wb") as f:
            f.write(fileSubmission.buffer)

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
        dataBasePath = GetDataBasePath()
        self.connection = sqlite3.connect(dataBasePath, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.dtName=  "record"
        self.boothNameTable = GetBoothNameTable()
        self.finishedColumnName = "Finished"
        self.attendedAllColumName = "AttenedAll"

        self.writeQueue = queue.Queue()
        self.threadLock = threading.Lock()
        self.queueThread = None

        self.CreateDataTable()

        self.unstructuredSaver = UnstructuredDataSaveUtility()

    def SubmissionFilePathToUserInfo(self, filePath):
        return self.unstructuredSaver.SubmissionFilePathToUserInfo(filePath)

    def EnqueUserUpdateBoothOnly(self, userInfos, boothName):
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

    def StopWriteThread(self):
        with self.threadLock:
            if self.writeQueue.empty() and self.queueThread.is_alive():
                self.writeQueue = None
                print("stoping write thread!")
        
    def ProcessQueue(self):
        while not self.writeQueue.empty():
            userUpdateInfo: UserUpdateInfo = self.writeQueue.get()
            print(f"process queued data:\n{userUpdateInfo}")
            try:
                self.AddOrUpdateUser(userUpdateInfo)
                self.unstructuredSaver.SaveSubmission(userUpdateInfo.fileSubmission)
            except sqlite3.OperationalError as e:
                print("=======================EORROR========================")
                print(f"error during write operation: {e}")
                print("=====================================================")

        self.StopWriteThread()

    def CreateDataTable(self):
        columnDefination = f'''id INTEGER PRIMARY KEY AUTOINCREMENT'''

        for col in GetUsrIdentiryColumnNames():
            columnDefination += f",\n{col} TEXT"

        for boothName in self.GetBoothNames():
            columnDefination += f",\n{boothName} INTEGER"

        columnDefination += f", \n{self.GetCompetitionColumnName()} TEXT"

        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {self.dtName} ({columnDefination})')

    def GetCompetitionColumnName(self):
        return "competitions"

    def GetInvalidInfos(self, info):
        InvalidInfo = []
        for i, inf in enumerate(info):
            if inf == "":
                InvalidInfo.append(i)

        return InvalidInfo

    def GetRecord(self, userInfos, recordColumNames="*"):
        query = self.BuildUserQuery(recordColumNames)
        self.cursor.execute(query, tuple(userInfos))
        user = self.cursor.fetchone()
        return user

    def BuildUserQuery(self, querycolumnName = "*"):
        queryFilters = self.ComposeUserQueryFilters()
        query = f'SELECT {querycolumnName} FROM {self.dtName} WHERE {queryFilters}'
        return query

    def GetUserRecordAsDataFrame(self, info):
        query = self.BuildUserQuery() 
        return pd.read_sql_query(query, self.connection, params=tuple(info))

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


    def AddOrUpdateUser(self, userUpdateInfo: UserUpdateInfo):
        record = self.GetRecord(userUpdateInfo.userInfos)
        if record:
            self.UpdateUser(userUpdateInfo)
        else:
            self.AddUser(userUpdateInfo)

    def AddUser(self, userUpdateInfo: UserUpdateInfo):
        if self.GetRecord(userUpdateInfo.userInfos):
            return

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
        self.cursor.execute(query,tuple(userUpdateInfo.userInfos))
        self.connection.commit()

        self.UpdateUserCompetitionEntry(userUpdateInfo)

    def GetBoothNames(self):
        return list(self.boothNameTable.values())

    def ComposeUserQueryFilters(self):
        queryFilterList = []
        for col in GetUsrIdentiryColumnNames():
            queryFilterList.append(f"{col}=?")

        return ' AND '.join(queryFilterList)


    def UpdateUser(self, userUpdateInfo: UserUpdateInfo):
        queryFilters = self.ComposeUserQueryFilters()
        boothUpdateQuery = f'UPDATE {self.dtName} Set {userUpdateInfo.boothName} = 1 WHERE {queryFilters}'
        self.cursor.execute(boothUpdateQuery, tuple(userUpdateInfo.userInfos))
        self.connection.commit()

        self.UpdateUserCompetitionEntry(userUpdateInfo)

    def UpdateUserCompetitionEntry(self, userUpdateInfo: UserUpdateInfo):
        """
        competition entires are stored as strings with each entry seperated by a comma:
        "entryOne,entryTwo"
        """

        if userUpdateInfo.fileSubmission.fileType == EFileSubmissionSaveType.NoType:
            return

        currentCompetitionEntriesStr = self.GetRecord(userUpdateInfo.userInfos, self.GetCompetitionColumnName())[0]
        print(f"{userUpdateInfo.userInfos[0]} currently has: {currentCompetitionEntriesStr} competition entires")
    
        newCompetitionEntry = userUpdateInfo.fileSubmission.savePath
        if currentCompetitionEntriesStr is not None and newCompetitionEntry in currentCompetitionEntriesStr:
            print(f"{newCompetitionEntry} is already in existing entiries: {currentCompetitionEntriesStr}")
            return

        #compose new competition entries as a str
        newCompetitionEntriesStr = newCompetitionEntry
        if currentCompetitionEntriesStr is not None:
            newCompetitionEntriesStr = f"{newCompetitionEntriesStr},{currentCompetitionEntriesStr}"

        # apply the change to the data base
        queryFilters = self.ComposeUserQueryFilters()
        competitionEntiresUpdateQuery = f'UPDATE {self.dtName} Set {self.GetCompetitionColumnName()} = ? WHERE {queryFilters}'
        competitionEntiresQueryParms = [newCompetitionEntriesStr] + userUpdateInfo.userInfos
        self.cursor.execute(competitionEntiresUpdateQuery, tuple(competitionEntiresQueryParms))
        self.connection.commit()

    def GetDataAsDataFrame(self):
        query = f"SELECT * FROM {self.dtName}"
        df = pd.read_sql_query(query, self.connection)
        print(df)
        BoothNames = self.GetBoothNames()

        df[self.finishedColumnName] = 0
        for boothName in BoothNames:
            df[self.finishedColumnName] += df[boothName]

        df[self.attendedAllColumName] = (df[self.finishedColumnName] == len(BoothNames)).astype(int)
        return df


    def SaveImageForUser(self, userInfos: list[str], boothName: str, image: Image):
        savePath = self.unstructuredSaver.ComposeSavePathForUser(userInfos, boothName, "jpg")
        saveBuff = BytesIO()        
        image.convert("RGB").save(saveBuff, "JPEG",quality=90, optimize=True)
        submissionInfo = FileSubmission(fileSaveType = EFileSubmissionSaveType.Photo, buffer = saveBuff.getvalue(), savePath = savePath)
        self.EnqueUserUpdate(UserUpdateInfo(userInfos, boothName, submissionInfo))



