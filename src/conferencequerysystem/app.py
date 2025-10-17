import streamlit as st
from conferencequerysystem.database import DataBase
from conferencequerysystem.fetch import GetUsersWithAttendedCountHigherThan
from conferencequerysystem.consts import GetAdminAccessCode, GetBoothNameTable, GetConferenceName, GetUsrDataCollectEntires, GetCompetitionType, ECompetitionSubmitType
from PIL import Image

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

    def CheckAndPromoteInvalidInfo(self, userInfos):
        invalidInfos = self.dataBase.GetInvalidInfos(userInfos)
        if invalidInfos == []:  
            return False


        st.markdown(f"<span style='color:red'>please fill in the missing fields:</span>", unsafe_allow_html=True)
        for invalidColIndex in invalidInfos:
            fieldName = GetUsrDataCollectEntires()[invalidColIndex].replace("_", " ")
            st.markdown(f"<span style='color:red'>{fieldName}</span>", unsafe_allow_html=True)

        return True


    def ConvertyBoothNameToDisplayName(self, boothName):
        return boothName.replace("_", " ")

    def ShowBoothGreeting(self, boothCode):
        boothName = GetBoothNameTable()[boothCode] 
        st.title(f"Welcome to {GetConferenceName()}!")
        boothDisplayName = self.ConvertyBoothNameToDisplayName(boothName)
        st.subheader(f"You are at the {boothDisplayName} booth")
        userInfos = []
        for userCol in GetUsrDataCollectEntires(): 
            colInfo = st.text_input(f"Enter your {userCol.replace("_", " ")}: ")
            userInfos.append(colInfo)

        if not self.CheckAndPromoteInvalidInfo(userInfos):
            self.DisplayUserInfo(userInfos)
            self.ShowUserSettings(userInfos, boothName)
            # self.ShowCompetitionStat(userInfos, boothName)


    def ShowUserSettings(self, userInfos, boothName):
        buttonLabel = "Register"
        if self.dataBase.HasUser(userInfos):
            buttonLabel = "Update"

        if st.button(buttonLabel):
            st.text(f"Thank you for registering!")
            self.dataBase.EnqueUserUpdate(userInfos, boothName)
            st.rerun()


    def ShowCompetitionStat(self, userInfos, boothName):
        competitionType = GetCompetitionType(boothName)
        if competitionType != ECompetitionSubmitType.NoType:
            competitionTypeName = competitionType.name
            st.subheader(f"submit your interactive work & win a prize!")
            st.text(f"how it works:")
            st.text(f"1, finish your interactive work\n2, Take a {competitionTypeName}:")
            if st.button(f"Take {competitionTypeName}"):
                if competitionType == ECompetitionSubmitType.Photo:
                    self.TakePhoto(userInfos, boothName)

                if competitionType == ECompetitionSubmitType.Video:
                    self.TakeVideo(userInfos, boothName)


    def TakePhoto(self, userInfos, boothName):
        print(f"taking photo for: {userInfos}, at booth {boothName}")
        # imageFileBuffer = st.camera_input("Take a picture")  
        # if(imageFileBuffer is not None):
        #     image = Image.open(imageFileBuffer)
        #     st.image(image, caption="your entry", use_column_width=True)

    def TakeVideo(self, userInfos, boothName):
        print(f"taking video for: {userInfos}, at booth {boothName}")

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
            st.subheader("Your Journey So Far:")
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
