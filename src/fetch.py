import subprocess
import os
from consts import GetScriptsDir, GetPrjDir, GetCSVOutputPath, GetBoothNameTable, GetOutputDir
import sqlite3
import pandas as pd

def FetchRemoteDataBase():
    shellCmdPath = os.path.join(GetScriptsDir(), "copyDataToLocal.sh")
    result = subprocess.run(['bash', shellCmdPath], capture_output=True, text=True)
    print(f"fetch remote return code: {result.returncode}")
    print(f"fetch output: {result.stdout}")
    if result.returncode != 0:
        print(f"error output: {result.stderr}")

def GetDataAsDf():
    query = f"SELECT * FROM record"
    return GetDfFromQuery(query)

def GetDFWithFilter(filter):
    query = f"SELECT * From record WHERE {filter}"
    return GetDfFromQuery(query)

def GetNamesWithAttendCountHigherThan(count):
    columns = list(GetBoothNameTable().values())
    filter = f"({'+'.join(columns)})>{count}"
    df = GetDFWithFilter(filter)
    if df is not None:
        df["name and school"] = df["name"] + " from " + df["school"]
        return df["name and school"].tolist()

    return []

def ConvertDataToCSV():
    df = GetDataAsDf()
    df.to_csv(GetCSVOutputPath())

def FetchAndConvertRemoteDataToCSV():
    FetchRemoteDataBase()
    ConvertDataToCSV()

def GetDfFromQuery(query):
    dataPath = os.path.join(GetPrjDir(), 'data.db')
    if os.path.exists(dataPath):
        connection = sqlite3.connect(dataPath, check_same_thread=False)
        df = pd.read_sql_query(query, connection)
        return df

    print("data.db does not exists, you can use the script/copyDataToLocal.sh to retreve it")
    return None

def WriteListToOutput(outputList, name, seperator=',', perline=True):
    outputPath = os.path.join(GetOutputDir(), name)
    fileContent = ""

    for item in outputList:
        fileContent += item + seperator
        if perline:
            fileContent += "\n"

    with open(outputPath, 'w') as file:
        file.write(fileContent)

if __name__ == "__main__":
    FetchAndConvertRemoteDataToCSV()
    names = GetNamesWithAttendCountHigherThan(3)
    WriteListToOutput(names, "biggerThan3.txt")
