import os

def GetPrjDir():
    scriptFilePath = os.path.abspath(__file__)
    srcDir = os.path.dirname(scriptFilePath)
    prjDir = os.path.dirname(srcDir)
    return os.path.normpath(prjDir) 

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

def GetUsrDataCollectEntires():
    return ["name", "occupation"] 

def GetBoothNameTable():
    return {
            'caf414ad66ab482c':"Ballroom_Animation",
            '983ebf1830cd4fd6':"Ballroom_Modeling",
            'fc9af05e1be9ad90':"Ballroom_Programming",
            '9345b7ac1ebf36fb':"Animation_Interactive",
            '3b35daf3e310fbbe':"Animation_Demo",
            '393d01f7ce7ee1a4':"Modeling_Interactive",
            'b20e98164a4df71d':"Modeling_Demo"
    }

def GetAdminAccessCode():
    return "ANGD4444UPGRADEVICTORIA"