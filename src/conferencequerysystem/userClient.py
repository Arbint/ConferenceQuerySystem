import streamlit as st
from pathlib import Path

from conferencequerysystem.database import DataBase
from conferencequerysystem.consts import (
                                          GetBoothNameTable,
                                          GetConferenceName,
                                          GetUsrIdentiryColumnNames,
                                          GetCompetitionType,
                                          ECompetitionSubmitType,
                                          GetAllowedExtensions
                                          )

class App:
    def __init__(self):
        self.dataBase = DataBase()

    def GetCode(self): 
        context=st.query_params
        return context.get("c", "")

    def Start(self):
        code = self.GetCode()
        self.ShowBoothGreeting(code)

    def ShowBoothGreeting(self, boothCode):
        boothName = GetBoothNameTable()[boothCode] 
        st.title(f"Welcome to {GetConferenceName()}!")
        boothDisplayName = self.ConvertyBoothNameToDisplayName(boothName)
        st.subheader(f"You are at the {boothDisplayName} booth")
        userInfos = []
        for userCol in GetUsrIdentiryColumnNames(): 
            colInfo = st.text_input(f"Enter your {userCol.replace("_", " ")}: ")
            userInfos.append(colInfo)

        if not self.CheckAndPromoteInvalidInfo(userInfos):
            self.DisplayUserInfo(userInfos)
            self.ShowUserSettings(userInfos, boothName)
            self.ShowCompetitionWidget(userInfos, boothName)

    def CheckAndPromoteInvalidInfo(self, userInfos):
        invalidInfos = self.dataBase.GetInvalidInfos(userInfos)
        if invalidInfos == []:  
            return False

        st.markdown(f"<span style='color:red'>please fill in the missing fields:</span>", unsafe_allow_html=True)
        for invalidColIndex in invalidInfos:
            fieldName = GetUsrIdentiryColumnNames()[invalidColIndex].replace("_", " ")
            st.markdown(f"<span style='color:red'>{fieldName}</span>", unsafe_allow_html=True)

        return True

    def ConvertyBoothNameToDisplayName(self, boothName):
        return boothName.replace("_", " ")


    def ShowUserSettings(self, userInfos, boothName):
        buttonLabel = "Register"
        if self.dataBase.HasUser(userInfos):
            buttonLabel = "Update"

        if st.button(buttonLabel):
            st.text(f"Thank you for registering!")
            self.dataBase.EnqueUserUpdateBoothOnly(userInfos, boothName)
            st.rerun()

    def ShowCompetitionWidget(self, userInfos, boothName):
        competitionType = GetCompetitionType(boothName)
        if competitionType == ECompetitionSubmitType.NoType:
            return

        st.subheader(f"submit your interactive work & win a prize!")
        st.text(f"how it works:")
        st.text(f"1,Finish your interactive work")
        st.text(f"2,User the widget below to upload")
        st.text(f"\tIf failed, refresh & retry")
        uploadedFile = st.file_uploader(f"Take/Upload a {competitionType.name}", type=GetAllowedExtensions(competitionType), accept_multiple_files=False)
        if uploadedFile:
            ext = Path(uploadedFile.name).suffix.lower()
            success, msg = self.dataBase.SaveSubmissionForUser(userInfos, boothName, uploadedFile.getvalue(), ext)
            if success:
                st.success("Upload Successful!")
            else:
                st.error(f"failed to upload: {msg}")


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
    

app = App()
app.Start()
