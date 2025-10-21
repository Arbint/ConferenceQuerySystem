import subprocess
import os
from conferencequerysystem.consts import GetAdminServerPort, GetClientServerPort, GetSubmissionServerPort

def LaunchStreamlitClientServer():
    fileDir = os.path.dirname(__file__)
    appPath = os.path.join(fileDir, "userClient.py")
    subprocess.Popen(["streamlit", "run", str(appPath), "--server.address=0.0.0.0", "--server.port", GetClientServerPort()])

def LaunchStreamlitSubmissionServer():
    fileDir = os.path.dirname(__file__)
    appPath = os.path.join(fileDir, "submissionViewClient.py")
    subprocess.Popen(["streamlit", "run", str(appPath),"--server.address=0.0.0.0", "--server.port", GetSubmissionServerPort()])

def LaunchStreamlitAdminServer():
    fileDir = os.path.dirname(__file__)
    appPath = os.path.join(fileDir, "adminClient.py")
    subprocess.run(["streamlit", "run", str(appPath), "--server.address=0.0.0.0", "--server.port", GetAdminServerPort()])

def LaunchStreamlitServers():
    LaunchStreamlitClientServer()
    LaunchStreamlitSubmissionServer()
    LaunchStreamlitAdminServer()
