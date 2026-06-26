import streamlit as st
import os

# 导入你 Day 3 写的 LLM 模块
from main import summarize, extract, rewrite
# 初始化历史记录
if "history" not in st.session_state:
    st.session_state.history = []

# ============ 页面配置 ============
st.set_page_config(
    page_title="AI 文本工具箱",
    page_icon="🛠️",
    layout="centered"
)

# ============ 侧边栏 ============
st.sidebar.title("🛠️ AI 文本工具箱")
st.sidebar.write("基于大语言模型的文本处理工具")
st.sidebar.divider()

# API Key 检查
api_key = os.environ.get("MOONSHOT_API_KEY", "")
if not api_key:
    st.sidebar.warning("⚠️ 未检测到 API Key，请在环境变量中设置 MOONSHOT_API_KEY")
else:
    st.sidebar.success("✅ API Key 已配置")

st.sidebar.divider()
st.sidebar.write("💡 提示：在左侧选择功能，粘贴文本，点击处理")

# ============ 主页面 ============
st.title("🛠️ AI 文本工具箱")
col1, col2 = st.columns([2, 1])
with col1:
    if st.button("处理", key="btn_process"):
        # 处理逻辑...
        pass
with col2:
    if st.button("清空", key="btn_clear"):
        st.session_state.summary_text = ""
        st.rerun()  # 重新运行，清空输入框
# 功能选择标签页
tab1, tab2, tab3,tab4 = st.tabs(["📝 摘要", "🔍 信息提取", "✏️ 风格改写","📊 统计"])

# ---- 标签页1：摘要 ----
with tab1:
    st.subheader("文本摘要")
    text = st.text_area(
        "输入要摘要的文本",
        height=200,
        placeholder="把长文本粘贴到这里...",
        key="summary_text"
    )
    if st.button("生成摘要", key="btn_summary"):
        if not text.strip():
            st.warning("请先输入文本！")
        elif not api_key:
            st.error("请先配置 API Key！")
        else:
            with st.spinner("正在生成摘要..."):
                try:
                    result = summarize(text)
                    st.success("摘要生成完成！")
                    st.write(result)
                except Exception as e:
                    st.error(f"出错了：{e}")

# ---- 标签页2：信息提取 ----
with tab2:
    st.subheader("信息提取")
    text = st.text_area(
        "输入要提取信息的文本",
        height=200,
        placeholder="把文本粘贴到这里，自动提取人名、日期、金额等...",
        key="extract_text"
    )
    if st.button("提取信息", key="btn_extract"):
        if not text.strip():
            st.warning("请先输入文本！")
        elif not api_key:
            st.error("请先配置 API Key！")
        else:
            with st.spinner("正在提取信息..."):
                try:
                    result = extract(text)
                    st.success("信息提取完成！")
                    st.write(result)
                except Exception as e:
                    st.error(f"出错了：{e}")

# ---- 标签页3：风格改写 ----
with tab3:
    st.subheader("风格改写")
    text = st.text_area(
        "输入要改写的文本",
        height=200,
        placeholder="把要改写的文本粘贴到这里...",
        key="rewrite_text"
    )
    style = st.selectbox(
        "选择目标风格",
        ["轻松口语", "正式商务", "学术严谨", "小红书风格", "幽默搞笑"]
    )
    if st.button("开始改写", key="btn_rewrite"):
        if not text.strip():
            st.warning("请先输入文本！")
        elif not api_key:
            st.error("请先配置 API Key！")
        else:
            with st.spinner(f"正在改写为「{style}」风格..."):
                try:
                    result = rewrite(text, style)
                    st.success("改写完成！")
                    st.write(result)
                except Exception as e:
                    st.error(f"出错了：{e}")
with tab4:
    st.subheader("字数统计")
    text = st.text_area(
        "输入要统计的文本",
        height=200,
        placeholder="把文本粘贴到这里，自动统计字数...",
        key="count_text"
    )
    if st.button("统计字数", key="btn_count"):
        if not text.strip():
            st.warning("请先输入文本！")
        else:
           #统计单词数
            st.write(f"单词数：{len(text.split())}")
           #统计段落数
            st.write(f"段落数：{len(text.split(chr(10)))}")#统计段落
           #统计字符数，不含空格
            st.write(f"字符数（不含空格）：{len(text.replace(' ', ''))}")
           #统计字符数，含空格
            st.write(f"字符数（含空格）：{len(text)}")


# 处理完成后，把结果存入历史
if 'result' in locals() and result:
    st.session_state.history.append({
        "mode": "摘要",
        "input": text[:50] + "...",
        "output": result[:100] + "..."
    })
# ============ 历史记录 ============
# 在侧边栏显示历史
st.sidebar.divider()
st.sidebar.subheader("📋 处理历史")

for i, record in enumerate(st.session_state.history[-5:]):  # 只显示最近5条
    
    st.sidebar.write(f" {record['mode']}:\n {record['output']}")


# ============ 页脚 ============
st.divider()
st.caption("AI 文本工具箱 | 基于 Kimi API + Streamlit | Day 5 学习项目")