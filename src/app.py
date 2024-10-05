import streamlit as st
from database import DataBase
from fetch import GetUsersWithAttendedCountHigherThan
from consts import GetAdminAccessCode, GetBoothNameTable, GetConferenceName, GetUsrDataCollectEntires

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
        st.title(f"Welcome to {GetConferenceName()}!")
        boothDisplayName = boothName.replace("_"," ")
        st.subheader(f"You are at the {boothDisplayName} booth")
        userInfos = []
        for userCol in GetUsrDataCollectEntires(): 
            colInfo = st.text_input(f"Enter your {userCol.replace("_", " ")}: ")
            userInfos.append(colInfo)

        self.DisplayUserInfo(userInfos)

        if st.button("Register"):
            invalidInfos = self.dataBase.GetInvalidInfos(userInfos)
            if invalidInfos == []:  
                st.text(f"Thank you for registering!")
                self.dataBase.EnqueUserUpdate(userInfos, boothName)
            else:
                invalidFields = ""
                for invalidColIndex in invalidInfos:
                    invalidFields += "\n" + GetUsrDataCollectEntires()[invalidColIndex].replace("_", " ")

                st.text(f"please fill in the missing field: {invalidFields}")

        if st.button("refresh"):
            st.rerun()
    
    def DisplayUserInfo(self, info):
        recordDf = self.dataBase.GetUserRecordAsDataFrame(info)
        if recordDf.empty:
            st.subheader("Press Register to Start Your Journey!")
            return

        visited, notVisited = self.dataBase.GetUserJourney(info)
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
        users = GetUsersWithAttendedCountHigherThan(number-1)
        st.dataframe(users)

app = App()
app.Start()
