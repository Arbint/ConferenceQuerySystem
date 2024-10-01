import streamlit as st
import queue
import threading

from record import GetBoothCodeMap, WriteRecord, GetRecord, ListToDisplayText

q=queue.Queue()

def WriteToDataWorker():
    while True:
        data = q.get()
        if data is None:
            continue

        name = data[0]
        booth = data[1]
        WriteRecord(name, booth)

workerThread = threading.Thread(target = WriteToDataWorker, daemon=True)
workerThread.start()

def DisplayUserInfo(userName):
    if not userName:
        return
    visited, notVisited = GetRecord(userName)

    st.subheader("You have visited:")
    st.text(ListToDisplayText(visited))

    st.subheader("you haven't visit:")
    st.text(ListToDisplayText(notVisited))

context=st.query_params
boothCode = context.get("c", "")
codeMap = GetBoothCodeMap()
boothName = codeMap[boothCode] 

st.title("Welcom to UPGRADE!")
st.subheader(f"you are at the {boothName} booth")
userName = st.text_input("Enter your name: ")
DisplayUserInfo(userName)

if st.button("Register"):
    if userName:
        st.text(f"Thank you for registering\n{userName}!")
        q.put([userName, boothName])
    else:
        st.text("name is empty, please put in your name!")

