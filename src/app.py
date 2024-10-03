import streamlit as st
from database import DataBase
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
        st.title("Welcom to UPGRADE!")
        st.subheader(f"You are at the {boothName.replace("_", " ")} booth")
        userName = st.text_input("Enter your name: ")
        self.DisplayUserInfo(userName)

        if st.button("Register"):
            if userName:
                st.text(f"Thank you for registering\n{userName}!")
                self.dataBase.EnqueUserUpdate(userName, boothName)
            else:
                st.text("name is empty, please put in your name!")

        if st.button("refresh"):
            st.rerun()
    

    def DisplayUserInfo(self, userName):
        recordDf = self.dataBase.GetUserRecordAsDataFrame(userName)
        if recordDf.empty:
            st.subheader("Press Register to Start Your Journey!")
            return

        visited, notVisited = self.dataBase.GetUserJourney(userName)
        visited = [x.replace("_"," ") for x in visited]
        notVisited = [x.replace("_"," ") for x in notVisited]
        if notVisited:
            st.subheader("You Journey So Far:")
            st.markdown("***You Have Visited:***")
            st.text(f"\n{'\n'.join(visited)}")
            st.markdown("***You Haven't Visit:***")
            st.text(f"\n{'\n'.join(notVisited)}")
        else:
            st.subheader("You have Finished Visiting All Booth!")
            st.text(f"you have visited:\n{'\n'.join(visited)}")

    def ShowAdmin(self):
        st.title("UPGRADE BOOTH STATUS")
        if st.button("refresh"):
            st.rerun()
        st.dataframe(self.dataBase.GetDataAsDataFrame())

app = App()
app.Start()
