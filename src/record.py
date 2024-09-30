import os
import pandas as pd

def GetRecordFileName():
    return "registerRecord.csv"

def GetRecordFilePath():
    scriptFilePath = os.path.abspath(__file__)
    srcDir = os.path.dirname(scriptFilePath)
    prjDir = os.path.dirname(srcDir)
    outputDir = os.path.join(prjDir, "output")
    return os.path.normpath(os.path.join(outputDir, GetRecordFileName()))

def GetNameColumnName():
    return "name"

def GetBoothColumnNames():
    return "modeling", "animation", "all"

def GetAllVisitedColumName():
    return "allVisited"

def GetRecord():
    recordFilePath = GetRecordFilePath()
    if not os.path.exists(recordFilePath):
        data = {
            GetNameColumnName() : []
        }

        for colName in GetBoothColumnNames():
            data[colName] = []

        df = pd.DataFrame(data)
        df.to_csv(recordFilePath)
        return df

    df = pd.read_csv(recordFilePath)

def WriteRecord(name, booth):
    record = GetRecord()
    print(record)
