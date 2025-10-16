import subprocess
import os

def LaunchStreamlitServer():
    fileDir = os.path.dirname(__file__)
    appPath = os.path.join(fileDir, "app.py")
    subprocess.run(["streamlit", "run", str(appPath)])
