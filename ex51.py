import html
import streamlit as st
from llm import call_llm

st.set_page_config(page_title="简易 ChatGPT", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown(
    """
    <style>
    .chat-wrap {
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
        margin-top: 1rem;
    }
    .msg-row {
        display: flex;
        width: 100%;
        margin-bottom: 0.2rem;
    }
    .msg-row.user {
        justify-content: flex-start;
    }
    .msg-row.assistant {
        justify-content: flex-end;
    }
    .bubble {
        max-width: 70%;
        padding: 0.75rem 1rem;
        border-radius: 16px;
        line-height: 1.5;
        white-space: pre-wrap;
        word-break: break-word;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
    }
    .bubble.user {
        background-color: #f1f3f5;
        color: #111;
        border-top-left-radius: 4px;
    }
    .bubble.assistant {
        background-color: #dcf8c6;
        color: #111;
        border-top-right-radius: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("菜单")
    if st.button("清空对话"):
        st.session_state.messages = []
        st.rerun()

st.title("简易 ChatGPT 聊天界面")
st.write("在下面输入问题，点击发送即可模拟与 AI 的对话。")

chat_container = st.container()

with chat_container:
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)

    for message in st.session_state.messages:
        role = message["role"]
        content = html.escape(message["content"])
        if role == "user":
            st.markdown(
                f'<div class="msg-row user">'
                f'<div class="bubble user">{content}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="msg-row assistant">'
                f'<div class="bubble assistant">{content}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown('</div>', unsafe_allow_html=True)

prompt = st.chat_input("请输入你的消息...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with chat_container:
        st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="msg-row user">'
            f'<div class="bubble user">{html.escape(prompt)}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    reply = call_llm(prompt)
    st.session_state.messages.append({"role": "assistant", "content": reply})

    with chat_container:
        st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="msg-row assistant">'
            f'<div class="bubble assistant">{html.escape(reply)}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)