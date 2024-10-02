import streamlit as st
import sqlite3

from database import DataBase

class App:
    def __init__(self):
        self.dataBase = DataBase()
        self.adminCode = "ANGD4444UPGRADEVICTORIA"

    def GetCode(self): 
        context=st.query_params
        return context.get("c", "")

    def Start(self):
        code = self.GetCode()
        if code == self.adminCode:
            self.ShowAdmin()
        else:
            self.ShowBoothGreeting(code)

    def ShowBoothGreeting(self, boothCode):
        boothName = self.dataBase.GetBoothTable()[boothCode] 
        st.title("Welcom to UPGRADE!")
        st.subheader(f"you are at the {boothName} booth")
        userName = st.text_input("Enter your name: ")
        self.DisplayUserInfo(userName)

        if st.button("Register"):
            if userName:
                st.text(f"Thank you for registering\n{userName}!")
                self.dataBase.EnqueUserUpdate(userName, boothName)
                st.rerun()
            else:
                st.text("name is empty, please put in your name!")

    def DisplayUserInfo(self, userName):
        recordDf = self.dataBase.GetUserRecordAsDataFrame(userName)
        if recordDf.empty:
            st.subheader("Press Register to Update your Jurney!")
            return

        visited, notVisited = self.dataBase.GetUserJurney(userName)
        visited = [x.replace("_"," ") for x in visited]
        notVisited = [x.replace("_"," ") for x in notVisited]
        if notVisited:
            st.subheader("You Jurney So Far:")
            st.text(f"you have visited: {' | '.join(visited)}")
            st.text(f"you haven't visit: {' | '.join(notVisited)}")
        else:
            st.subheader("You have Finished Visiting All Booth!")
            st.text(f"you have visited: {' | '.join(visited)}")

    def ShowAdmin(self):
        st.title("UPGRADE BOOTH STATUS")
        st.dataframe(self.dataBase.GetDataAsDataFrame())

app = App()
app.Start()
