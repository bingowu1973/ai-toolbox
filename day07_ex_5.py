import streamlit as st
from llm import call_llm
# 初始化 session_state 中的对话历史
if "messages" not in st.session_state:
    st.session_state.messages = []
# 页面配置
st.set_page_config(page_title="AI 聊天助手", page_icon="🤖")


# 侧边栏设置
with st.sidebar:
    st.title("聊天机器人设置")
    # 显示当前对话的轮数统计（一轮包含用户和AI各一条消息，所以除以2,但要排除第一条问候）
     
    if len(st.session_state.messages) > 0:

        st.write(f"当前对话轮数: {(len(st.session_state.messages)+1) // 2}")
    
    # 清空对话按钮
    if st.button("清空对话"):
        st.session_state.messages = []
        st.rerun()

# 首次打开时显示欢迎消息
if len(st.session_state.messages) == 0:
    st.session_state.messages.append({"role": "assistant", "content": "你好！我是你的 AI 聊天助手，有什么我可以帮助你的吗？"})

# 显示对话历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 接收用户输入
if prompt := st.chat_input("请输入你的消息..."):
    # 将用户消息添加到历史并显示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 模拟 AI 回复（带记忆效果：将之前的对话内容拼接作为上下文）
    with st.chat_message("assistant"):
        # 构建上下文，让 AI 能"记住"之前说过的内容
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
        # 调用 LLM 获取 AI 回复
        response = call_llm(prompt)
        # 显示 AI 回复

        #response = f"（我记住了我们之前的对话）你刚才说了：{prompt}。我们的对话上下文长度为：{len(st.session_state.messages)}。"
        st.markdown(response)
    
    # 将 AI 回复添加到历史记录
    st.session_state.messages.append({"role": "assistant", "content": response})

