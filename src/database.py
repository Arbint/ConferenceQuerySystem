import sqlite3
import os
import pandas as pd
import threading
import queue
from consts import GetBoothNameTable, GetDataBasePath, GetUsrDataCollectEntires

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

    def EnqueUserUpdate(self, info, visitedBooth):
        """
        ## Called by front end to update or add a user
        ***arguments:*** 
        * info(list(str)): user name, and all other infomations like (school, occupation, from, etc), used to find a user or add a user
        * visitedBooth(str): the booth the user has visited

        ***return:***

        None
        """

        self.writeQueue.put([info, visitedBooth])
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
                self.worker_thread = None
                print("stoping write thread!")
        
    def ProcessQueue(self):
        while not self.writeQueue.empty():
            data = self.writeQueue.get()
            print(f"process queued data: {data}")
            try:
                self.AddOrUpdateUser(data[0], data[1])
            except sqlite3.OperationalError as e:
                print("=======================EORROR========================")
                print(f"error during write operation: {e}")
                print("=====================================================")

        self.StopWriteThread()

    def CreateDataTable(self):
        columnDefination = f'''id INTEGER PRIMARY KEY AUTOINCREMENT'''

        for col in GetUsrDataCollectEntires():
            columnDefination += f",\n{col} TEXT"

        for boothName in self.GetBoothNames():
            columnDefination += f",\n{boothName} INTEGER"

        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {self.dtName} ({columnDefination})')

    def GetRecord(self, info):
        query = self.BuildUserQuery()
        self.cursor.execute(query, tuple(info))
        user = self.cursor.fetchone()
        return user

    def BuildUserQuery(self):
        queryFilterList = []
        for col in GetUsrDataCollectEntires():
            queryFilters.append(f" {col}=?")

        queryFilters = 'AND'.join(queryFilterList)
        query = f'SELECT * FROM {self.dtName} WHERE {queryFilterList}'
        print(f"query is: {query}")
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

    def AddOrUpdateUser(self, info, visitedBooth):
        record = self.GetRecord(info)
        if record:
            self.UpdateUser(info, visitedBooth)
        else:
            self.AddUser(info, visitedBooth)

    def AddUser(self, info, visitedBooth):
        if self.GetRecord(info):
            return

        colNames = GetUsrDataCollectEntires() 
        values = []

        boothNames = list(self.boothNameTable.values())
        for boothName in boothNames: 
            colNames.append(boothName)
            if boothName == visitedBooth:
                values.append('1')
            else:
                values.append('0')

        infoColValuesPlaceHolders = ""
        for i in range(len(GetUsrDataCollectEntires())):
            infoColValuesPlaceHolders += "?,"

        query = f'INSERT INTO {self.dtName} ({",".join(colNames)}) VALUES ({infoColValuesPlaceHolders} {",".join(values)})'
        self.cursor.execute(query,tuple(info))
        self.connection.commit()

    def GetBoothNames(self):
        return list(self.boothNameTable.values())

    def UpdateUser(self, info, newVisitedBooth):
        queryFilterList = []
        for col in GetUsrDataCollectEntires():
            queryFilters.append(f" {col}=?")

        queryFilters = 'AND'.join(queryFilterList)
        query = f'UPDATE {self.dtName} Set {newVisitedBooth} = 1 WHERE {queryFilterList}'
        print(f"query is: {query}")

        print(query)
        self.cursor.execute(query, tuple(info))
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
