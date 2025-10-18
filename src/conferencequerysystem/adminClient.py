import streamlit as st
from pathlib import Path

from conferencequerysystem.database import DataBase
from conferencequerysystem.fetch import GetUsersWithAttendedCountHigherThan
from conferencequerysystem.consts import GetAdminAccessCode

class App:
    def __init__(self):
        self.dataBase = DataBase()
        self.adminTabName = "UPGRADE BOOTH STATUS"
        self.submissionTypeSubfix = " Submissions"
        self.submissionDisplayColumnCount = 4
        self.submissionTabRefreshInterval = 5000

    def GetCode(self): 
        context=st.query_params
        return context.get("c", "")

    def Start(self):
        code = self.GetCode()
        if code != GetAdminAccessCode():
            return

        st.header(self.adminTabName)
        if st.button("refresh"):
            st.rerun()

        st.dataframe(self.dataBase.GetDataAsDataFrame())
        number = st.number_input("Filter Total Visit Bigger Than or Equal to:", min_value = 0, value=7, step=1)
        users = GetUsersWithAttendedCountHigherThan(number-1)
        st.dataframe(users)

app = App()
app.Start()
