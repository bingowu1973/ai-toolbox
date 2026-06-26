import streamlit as st  
#侧边栏：一个 selectbox 让用户选择"中文"/"英文"/"日文"
language = st.sidebar.selectbox("选择语言", ["中文", "英文", "日文"])
#主页面：根据选择的语言，显示对应的问候语（中文→你好，英文→Hello，日文→こんにちは）
if language == "中文":
    greeting = "你好"
elif language == "英文":
    greeting = "Hello"   
elif language == "日文":
    greeting = "こんにちは"
#一个 text_input 让用户输入自己的名字
name = st.text_input("请输入你的名字：")
#一个 button 让用户点击，点击后显示"你好，[用户输入的名字]"
if st.button("点击"):
    st.write(f"{greeting}，{name}")



 
 


