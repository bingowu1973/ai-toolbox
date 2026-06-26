import streamlit as st
from llm import call_llm

st.set_page_config(page_title="简易 ChatGPT", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("菜单")
    if st.button("清空对话"):
        st.session_state.messages = []
        st.rerun()

st.title("简易 ChatGPT 聊天界面")
st.write("在下面输入问题，点击发送即可模拟与 AI 的对话。")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("请输入你的消息...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reply = call_llm(prompt)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)