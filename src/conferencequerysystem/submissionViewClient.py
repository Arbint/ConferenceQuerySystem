import streamlit as st
from streamlit_autorefresh import st_autorefresh
from pathlib import Path

from conferencequerysystem.database import DataBase
from conferencequerysystem.fetch import GetUsersWithAttendedCountHigherThan
from conferencequerysystem.consts import (GetAdminAccessCode,
                                          GetBoothNameTable,
                                          GetConferenceName,
                                          GetUsrIdentiryColumnNames,
                                          GetCompetitionType,
                                          ECompetitionSubmitType,
                                          GetCompetitionBoothInfo,
                                          GetSubmissionsForBooth,
                                          GetAllowedExtensions
                                          )

class App:
    def __init__(self):
        self.dataBase = DataBase()
        self.submissionTypeSubfix = " Submissions"
        self.submissionDisplayColumnCount = 4
        self.submissionTabRefreshInterval = 5000
        self.autoRefreshKey = "live_tab_refresh"

    def GetCode(self): 
        context=st.query_params
        return context.get("c", "")

    def Start(self):
        code = self.GetCode()
        if code != GetAdminAccessCode():
            return

        st_autorefresh(interval=self.submissionTabRefreshInterval, key=self.autoRefreshKey)

        self.ShowSubmissionTabs()

    def ConvertyBoothNameToDisplayName(self, boothName):
        return boothName.replace("_", " ")

    def ShowSubmissionTabs(self):
        competitionBoothNames = list(GetCompetitionBoothInfo().keys())
        tabNames = [tabName.replace("_Interactive", self.submissionTypeSubfix) for tabName in competitionBoothNames]

        tabs = st.tabs(tabNames)

        for tab, name in zip(tabs, tabNames):
            with tab:
                st.header(name)
                boothName = self.GetBoothNameFromSubmissionTabName(name)
                self.ShowSubmissionsForBooth(boothName)

    def GetBoothNameFromSubmissionTabName(self, tabName: str):
        competitionBoothNames = list(GetCompetitionBoothInfo().keys())
        for boothName in competitionBoothNames:
            categoryName = tabName.replace(self.submissionTypeSubfix, "")
            if categoryName in boothName:
                return boothName

    def ShowSubmissionsForBooth(self, boothName):
        if st.button(f"refresh {boothName.replace("_", " ")}"):
            st.rerun()

        files = GetSubmissionsForBooth(boothName)
        fileType = GetCompetitionType(boothName)
        cols = st.columns(self.submissionDisplayColumnCount)
        for i, filePath in enumerate(files):
            with cols[i%self.submissionDisplayColumnCount]:
                filePathStr = str(filePath)
                captionName = self.dataBase.SubmissionFilePathToUserInfo(filePathStr)
                if fileType == ECompetitionSubmitType.Photo:
                    st.image(filePathStr, caption=captionName, use_column_width=True)
                if fileType == ECompetitionSubmitType.Video:
                    st.video(filePathStr, autoplay=True, loop=True)
                    st.caption(captionName)

app = App()
app.Start()
