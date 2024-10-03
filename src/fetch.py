from database import DataBase
import subprocess
import os
from consts import GetScriptsDir

def FetchRemoteDataBase():
    shellCmdPath = os.path.join(GetScriptsDir(), "copyDataToLocal.sh")
    result = subprocess.run(['bash', shellCmdPath], capture_output=True, text=True)
    print(f"fetch remote return code: {result.returncode}")
    print(f"fetch output: {result.stdout}")
    if result.returncode != 0:
        print(f"error output: {result.stderr}")

def ConvertRemoteDataToCSV():
    DataBase.ConvertDataToCSV()


def FetchAndConverRemoteDataToCSV():
    FetchRemoteDataBase()
    ConvertRemoteDataToCSV()

if __name__ == "__main__":
    FetchAndConverRemoteDataToCSV()