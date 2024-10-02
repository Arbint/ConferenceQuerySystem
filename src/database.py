import sqlite3
import os
import pandas as pd
import threading
import queue

def GetOutputDir():
    scriptFilePath = os.path.abspath(__file__)
    srcDir = os.path.dirname(scriptFilePath)
    prjDir = os.path.dirname(srcDir)
    outputDir = os.path.join(prjDir, "output")
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)

    return outputDir

def GetRecordCSVFilePath():
    return os.path.normpath(os.path.join(GetOutputDir(), "report.csv"))

class DataBase:
    def __init__(self):
        self.connection = sqlite3.connect('data.db', check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.dtName=  "record"
        self.boothNameTable = {
            'angd1331':"Animation",
            'angd1341':"Modeling",
            'angd1371':"Programming"
        }
        self.finishedColumnName = "Finished"
        self.attendedAllColumName = "AttenedAll"
        self.dataSavePath = ""

        self.writeQueue = queue.Queue()
        self.threadLock = threading.Lock()
        self.queueThread = None

        self.CreateDataTable()

    def EnqueUserUpdate(self, name, visitedBooth):
        self.writeQueue.put([name, visitedBooth])
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

    def GetBoothTable(self):
        return self.boothNameTable

    def CreateDataTable(self):
        columnDefination = f'''id INTEGER PRIMARY KEY AUTOINCREMENT,\nname TEXT UNIQUE'''

        for boothName in self.boothNameTable.values():
            columnDefination += f",\n{boothName} INTEGER"

        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {self.dtName} ({columnDefination})')

    def GetRecordByName(self, name):
        self.cursor.execute(f'SELECT * FROM {self.dtName} WHERE name = ?', (name,))
        user = self.cursor.fetchone()
        return user

    def GetUserRecordAsDataFrame(self, name):
        query = f"SELECT * FROM {self.dtName} WHERE name = ?"
        return pd.read_sql_query(query, self.connection, params=(name,))

    def GetUserJurney(self, name):
        df = self.GetUserRecordAsDataFrame(name)
        visited = []
        notVisited = self.GetBoothNames()
        if df.empty:
            return visited, notVisited

        for boothName in self.GetBoothNames():
            if df[boothName].values[0] == 1:
                visited.append(boothName) 
                notVisited.remove(boothName)
        return visited, notVisited

    def AddOrUpdateUser(self, name, visitedBooth):
        record = self.GetRecordByName(name)
        if record:
            self.UpdateUser(name, visitedBooth)
        else:
            self.AddUser(name, visitedBooth)

    def AddUser(self, name, visitedBooth):
        if self.GetRecordByName(name):
            return

        print(f"adding new user: {name}")
        colNames = ["name"]
        values = []

        boothNames = list(self.boothNameTable.values())
        for boothName in boothNames: 
            colNames.append(boothName)
            if boothName == visitedBooth:
                values.append('1')
            else:
                values.append('0')

        query = f'INSERT INTO {self.dtName} ({','.join(colNames)}) VALUES (?, {','.join(values)})'
        self.cursor.execute(query,(name,))
        self.connection.commit()

    def GetBoothNames(self):
        return list(self.boothNameTable.values())

    def UpdateUser(self, name, newVisitedBooth):
        print(f"updating user: {name} with new booth: {newVisitedBooth}")
        
        query = f'UPDATE {self.dtName} SET {newVisitedBooth} = 1 WHERE name=?'
        print(query)
        self.cursor.execute(query, (name,))
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

    def SaveDataToCSV(self):
        df = self.GetDataAsDataFrame()
        df.to_csv(GetRecordCSVFilePath())