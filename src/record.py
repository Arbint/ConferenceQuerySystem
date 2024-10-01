import os
import json
import pandas as pd

def GetBoothCodeMap():
    return {"0010111":"modeling", "1123338":"animation"}

def GetRecordJsonFileName():
    return "registerRecord.json"

def GetRecordCSVFileName():
    return "registerRecord.csv"

def GetBoothNames():
    return list(GetBoothCodeMap().values())

def GetOutputDir():
    scriptFilePath = os.path.abspath(__file__)
    srcDir = os.path.dirname(scriptFilePath)
    prjDir = os.path.dirname(srcDir)
    outputDir = os.path.join(prjDir, "output")
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)

    return outputDir

def GetRecordJsonFilePath():
    return os.path.normpath(os.path.join(GetOutputDir(), GetRecordJsonFileName()))

def GetRecordCSVFilePath():
    return os.path.normpath(os.path.join(GetOutputDir(), GetRecordCSVFileName()))

def GetNameColumnName():
    return "name"

def GetAllVisitedColumName():
    return "allVisited"

def GetRecord(name):
    visitedList = []
    notVisitedList = GetBoothNames()

    recordFilePath = GetRecordJsonFilePath()
    if not os.path.exists(recordFilePath):
        return visitedList, notVisitedList

    with open(recordFilePath, 'r') as recordJsonFile:
        data = json.load(recordJsonFile) 
        if name in data:
            visitedList = data[name]

    for visited in visitedList:
        notVisitedList.remove(visited)

    return visitedList, notVisitedList

def ListToDisplayText(inList):
    outText = ""
    for item in inList:
        outText += "\n"+item 

    return outText

def WriteRecord(name, booth):
    data = {name:[booth]}
    recordFilePath = GetRecordJsonFilePath()
    if not os.path.exists(recordFilePath):
        with open(recordFilePath, 'w') as recordJsonFile:
            json.dump(data, recordJsonFile, indent=2)
    else:
        with open(recordFilePath, 'r') as recordJsonFile:
            data = json.load(recordJsonFile) 
            if name in data: 
                if booth not in data[name]:
                   data[name].append(booth) 
            else:
                data[name] =[booth]
            

        with open(recordFilePath, 'w') as recordJsonFile:
            json.dump(data, recordJsonFile, indent=2)

    csvData = []
    for name, boothes in data.items():
        userData = {"name":name}
        all = 1 
        for boothName in GetBoothNames():
            if boothName in boothes:
                userData[boothName] = 1
            else:
                userData[boothName] = 0
                all = 0

        userData["all"] = all
        csvData.append(userData)

    df = pd.DataFrame(csvData)

    csvPath = GetRecordCSVFilePath()
    df.to_csv(csvPath, index=False)