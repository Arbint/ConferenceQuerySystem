import os
from pathlib import Path
from enum import Enum

class ECompetitionSubmitType(Enum):
    Photo = 1
    Video = 2
    NoType = 3

def GetConferenceName():
    return "UPGRADE"

def GetPrjDirRelative():
    scriptFilePath = os.path.abspath(__file__)
    moduleDir = os.path.dirname(scriptFilePath)
    srcDir = os.path.dirname(moduleDir)
    prjDir = os.path.dirname(srcDir)
    return os.path.normpath(prjDir) 

def GetPrjDirByPyprojectToml():
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if(parent/"pyproject.toml").is_file():
            return parent

    raise FileNotFoundError(f"trying to resolve the project root path by looking for the directory that contains the pyproject.toml file, but cannot find one")

def GetPrjDir():
    try:
        return GetPrjDirByPyprojectToml()
    except FileExistsError as e:
        print(f"{e}, trying to now use the relative path to find the root dir")
        return GetPrjDirRelative()

def GetScriptsDir():
    return os.path.join(GetPrjDir(), "scripts")

def GetAssetDir():
    return os.path.join(GetPrjDir(), "assets")

def GetOutputDir():
    prjDir = GetPrjDir() 
    outputDir = os.path.normpath(os.path.join(prjDir, "output"))
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)

    return outputDir

def GetCSVOutputPath():
    path = os.path.join(GetOutputDir(), "csvs")
    if not os.path.exists(path):
        os.mkdir(path)

    return os.path.normpath(os.path.join(path, "data.csv"))

def GetDataBasePath():
    return os.path.normpath(os.path.join(GetPrjDir(), "data.db"))

def GetUsrDataCollectEntires():
    return ["name", "school", "occupation"] 

def GetBoothNameTable():
    return {
            'caf414ad66ab482c':"Ballroom_Animation",
            '983ebf1830cd4fd6':"Ballroom_Modeling",
            'fc9af05e1be9ad90':"Ballroom_Programming",
            '9345b7ac1ebf36fb':"Animation_Interactive",
            '3b35daf3e310fbbe':"Animation_Demo",
            '393d01f7ce7ee1a4':"Modeling_Interactive",
            'b20e98164a4df71d':"Modeling_Demo",
            '2d6c9859a3a15919':"Programming_Interactive",
            'b20e98164a4df71d':"Programming_Demo"
    }

def GetCompetitionType(boothName):
    if boothName in GetCompetitionBoothInfo():
        return GetCompetitionBoothInfo()[boothName]

    return ECompetitionSubmitType.NoType

def GetCompetitionBoothInfo():
    return {
                "Modeling_Interactive": ECompetitionSubmitType.Photo,
                "Animation_Interactive": ECompetitionSubmitType.Video
           }

def GetAdminAccessCode():
    return "ANGD4444UPGRADEVICTORIA"