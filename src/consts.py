import os

def GetPrjDir():
    scriptFilePath = os.path.abspath(__file__)
    srcDir = os.path.dirname(scriptFilePath)
    prjDir = os.path.dirname(srcDir)
    return os.path.normpath(prjDir) 

def GetAssetDir():
    return os.path.join(GetPrjDir(), "assets")

def GetOutputDir():
    prjDir = GetPrjDir() 
    outputDir = os.path.normpath(os.path.join(prjDir, "output"))
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)

    return outputDir

def GetBoothNameTable():
    return {
            '2b7d2f56fbaf5f56':"Animation",
            'dd4d10e605e54b48':"Modeling",
            'db702f38d9ae126e':"Programming"
    }

def GetAdminAccessCode():
    return "ANGD4444UPGRADEVICTORIA"