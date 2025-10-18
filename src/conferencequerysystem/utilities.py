import os
import sys
from urllib.parse import urlparse

def SupprtGUI():
    # On Windows and macOS, GUI usually works by default.
    if sys.platform.startswith("win") or sys.platform == "darwin":
        return True

    # On Linux/Unix — check for DISPLAY environment variable.
    return "DISPLAY" in os.environ

def IsValidURL(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
    

def GetURLFromUser(msg: str):
    url = AskForURL(msg) 
    while not IsValidURL(url):
        url = AskForURL(f"Invalid URL!\n{msg}")

    return url


def AskForURL(msg=""):
    if SupprtGUI():
        from tkinter import simpledialog, Tk
        root = Tk()
        root.withdraw()
        
        label = "Please Enter a URL:"
        if msg != "":
            label = f"{msg}, {label}"

        url = simpledialog.askstring(msg, label)

        root.destroy()
        return url
    else:
        print(msg)
        return input(f"Player Enter a URL:")


