import streamlit as st
from record import GetRoomCodeMap, WriteRecord
context=st.query_params
boothCode = context.get("c", [""])
print(type(boothCode))
codeMap = GetRoomCodeMap()
boothName = codeMap[boothCode]

st.title("Welcom to UPGRADE!")
st.text(f"you are at the {boothName} booth")
userName = st.text_input("Enter your name: ")
if st.button("Register"):
    if userName:
        st.text(f"Thank you for registering\n{userName}!")
        WriteRecord(userName, boothName)
    else:
        st.text("name is empty, please put in your name!")

