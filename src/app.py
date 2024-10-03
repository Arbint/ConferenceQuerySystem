import streamlit as st
from database import DataBase
from fetch import GetNamesWithAttendCountHigherThan
from consts import GetAdminAccessCode, GetBoothNameTable

class App:
    def __init__(self):
        self.dataBase = DataBase()

    def GetCode(self): 
        context=st.query_params
        return context.get("c", "")

    def Start(self):
        code = self.GetCode()
        if code == GetAdminAccessCode():
            self.ShowAdmin()
        else:
            self.ShowBoothGreeting(code)

    def ShowBoothGreeting(self, boothCode):
        boothName = GetBoothNameTable()[boothCode] 
        st.title("Welcome to UPGRADE!")
        boothDisplayName = boothName.replace("_"," ")
        st.subheader(f"You are at the {boothDisplayName} booth")
        userName = st.text_input("Enter your name: ")
        schoolName = st.text_input("Enter your school: ")
        self.DisplayUserInfo(userName, schoolName)

        if st.button("Register"):
            if userName and schoolName:
                st.text(f"Thank you for registering\n{userName}!")
                self.dataBase.EnqueUserUpdate(userName, schoolName, boothName)
            elif not userName:
                st.text("name is empty, please fill in your name!")
            else:
                st.text("school is empty, please fill in your school!")

        if st.button("refresh"):
            st.rerun()
    

    def DisplayUserInfo(self, userName, schoolName):
        recordDf = self.dataBase.GetUserRecordAsDataFrame(userName, schoolName)
        if recordDf.empty:
            st.subheader("Press Register to Start Your Journey!")
            return

        visited, notVisited = self.dataBase.GetUserJourney(userName, schoolName)
        visited = [x.replace("_"," ") for x in visited]
        notVisited = [x.replace("_"," ") for x in notVisited]
        visitedDisplayText = '\n'.join(visited)
        notVisitedDisplayText = '\n'.join(notVisited)
        if notVisited:
            st.subheader("You Journey So Far:")
            st.markdown("***You Have Visited:***\n")
            st.text(visitedDisplayText)
            st.markdown("***You Haven't Visit:***\n")
            st.text(notVisitedDisplayText)
        else:
            st.subheader("You have Finished Visiting All Booth!")
            st.text(visitedDisplayText)

    def ShowAdmin(self):
        st.title("UPGRADE BOOTH STATUS")
        if st.button("refresh"):
            st.rerun()
        st.dataframe(self.dataBase.GetDataAsDataFrame())
        number = st.number_input("Filter Total Visit Bigger Than or Equal to:", min_value = 0, value=7, step=1)
        names = GetNamesWithAttendCountHigherThan(number-1)
        namesDisplayText = ""
        for name in names:
            namesDisplayText += name + "\n"
        st.text(namesDisplayText)

app = App()
app.Start()
