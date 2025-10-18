import subprocess
import os
from conferencequerysystem.consts import GetAdminServerPort, GetClientServerPort, GetSubmissionServerPort

def LaunchStreamlitClientServer():
    fileDir = os.path.dirname(__file__)
    appPath = os.path.join(fileDir, "userClient.py")
    subprocess.Popen(["streamlit", "run", str(appPath), "--server.port", GetClientServerPort()])

def LaunchStreamlitAdminServer():
    fileDir = os.path.dirname(__file__)
    appPath = os.path.join(fileDir, "adminClient.py")
    subprocess.Popen(["streamlit", "run", str(appPath), "--server.port", GetAdminServerPort()])

def LaunchStreamlitSubmissionServer():
    fileDir = os.path.dirname(__file__)
    appPath = os.path.join(fileDir, "submissionViewClient.py")
    subprocess.Popen(["streamlit", "run", str(appPath), "--server.port", GetSubmissionServerPort()])

def LaunchStreamlitServers():
    LaunchStreamlitAdminServer()
    LaunchStreamlitClientServer()
    LaunchStreamlitSubmissionServer()