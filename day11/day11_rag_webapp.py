"""
Day11 - 终极Boss：RAG 知识库问答网页应用
========================================
整合前4个模块的所有功能，做一个完整的知识库问答系统。

功能清单：
  ✅ 侧边栏上传文档（txt/md），构建向量知识库
  ✅ 侧边栏配置 RAG 参数（chunk_size、top_k、temperature）
  ✅ 流式输出（打字机效果）
  ✅ 聊天历史管理（session_state + 清空）
  ✅ 防幻觉（文档里没有的问题，模型要说"根据文档无法回答"）

运行方式：
  streamlit run day11_rag_webapp.py

前置条件：
  - Ollama 在运行（embedding 模型：qllama/bge-small-zh-v1.5:q4_k_m）
  - pip install streamlit openai langchain langchain-community langchain-text-splitters faiss-cpu
  - Kimi API Key（在侧边栏输入）
"""

import os
import json
import streamlit as st
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 知识库持久化目录
KB_DIR = Path("./knowledge_base")
KB_DIR.mkdir(exist_ok=True)

# ================================================================
# 第一部分：页面配置
# ================================================================
st.set_page_config(
    page_title="RAG 知识库问答",
    page_icon="📚",
    layout="wide",          # 宽屏布局
    initial_sidebar_state="expanded"  # 侧边栏默认展开
)

# ================================================================
# 第二部分：初始化 session_state（跨交互的状态存储）
# ================================================================
# messages：聊天历史消息列表
if "messages" not in st.session_state:
    st.session_state.messages = []

# vector_db：向量数据库（知识库）
if "vector_db" not in st.session_state:
    st.session_state.vector_db = None

# uploaded_content：已上传文档的内容缓存
if "uploaded_content" not in st.session_state:
    st.session_state.uploaded_content = ""

# doc_name：已上传文档名称
if "doc_name" not in st.session_state:
    st.session_state.doc_name = ""

# 启动时自动加载已保存的知识库
if "vector_db" not in st.session_state or st.session_state.vector_db is None:
    kb_meta_file = KB_DIR / "meta.json"
    if kb_meta_file.exists():
        try:
            with open(kb_meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
            embeddings = OllamaEmbeddings(
                model=meta.get("model", "qllama/bge-small-zh-v1.5:q4_k_m")
            )
            st.session_state.vector_db = FAISS.load_local(
                str(KB_DIR / "faiss_index"),
                embeddings,
                allow_dangerous_deserialization=True
            )
            st.session_state.doc_name = meta.get("doc_name", "")
            st.session_state.uploaded_content = meta.get("content", "")
        except Exception as e:
            st.session_state.vector_db = None

# ================================================================
# 第三部分：侧边栏 — 文件上传 + 参数配置
# ================================================================
with st.sidebar:
    st.title("📚 RAG 知识库问答")
    st.markdown("---")

    # ----- API Key 配置 -----
    st.subheader("🔑 API 配置")
    api_key = st.text_input(
        "Kimi API Key",
        type="password",
        value=os.environ.get("MOONSHOT_API_KEY", ""),
        help="从 https://platform.moonshot.cn/console/api-keys 获取"
    )

    st.markdown("---")

    # ----- 文件上传 -----
    st.subheader("📁 文档管理")
    uploaded_file = st.file_uploader(
        "上传文档",
        type=["txt", "md"],
        help="支持 TXT 和 Markdown 格式"
    )

    # 读取文件内容（存到 session_state，避免切换页面丢失）
    if uploaded_file is not None:
        raw = uploaded_file.read()
        # 自动检测编码：先utf-8，失败则gbk（兼容Windows中文文件）
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            content = raw.decode("gbk", errors="replace")
        st.session_state.uploaded_content = content
        st.session_state.doc_name = uploaded_file.name
        st.success(f"✅ 已加载：{uploaded_file.name}")
        st.caption(f"📊 {len(content)} 字符 | {content.count(chr(10))+1} 行")

        # 预览文档内容
        with st.expander("👀 预览文档"):
            st.markdown(content[:2000])
            if len(content) > 2000:
                st.caption(f"... 共 {len(content)} 字符，仅展示前 2000 字符")

    st.markdown("---")

    # ----- RAG 参数配置 -----
    st.subheader("⚙️ RAG 参数")

    col1, col2 = st.columns(2)
    with col1:
        chunk_size = st.slider("chunk_size", 100, 1000, 300, 50,
                               help="每个文档片段的字符数")
    with col2:
        chunk_overlap = st.slider("overlap", 0, 200, 50, 10,
                                  help="相邻片段的重叠字符数")

    top_k = st.slider("top_k（检索片段数）", 1, 10, 3,
                      help="每次问答检索多少个最相关的片段")

    temperature = st.slider("temperature", 0.0, 1.0, 0.0, 0.1,
                            help="0=严谨事实，1=创意发散")

    st.markdown("---")

    # ----- 构建知识库按钮 -----
    st.subheader("🚀 知识库操作")

    if st.button("🔨 构建知识库", use_container_width=True, type="primary"):
        # 检查是否已上传文档
        if not st.session_state.uploaded_content:
            st.warning("⚠️ 请先上传文档！")
        elif not api_key:
            st.warning("⚠️ 请先输入 Kimi API Key！")
        else:
            with st.spinner("正在构建知识库，请稍候..."):
                try:
                    # Step 1：创建 Document 对象
                    doc = Document(
                        page_content=st.session_state.uploaded_content,
                        metadata={"source": st.session_state.doc_name}
                    )

                    # Step 2：切分文档
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap,
                        separators=["\n\n", "\n", "。", "！", "？", ".", " ", ""]
                    )
                    chunks = text_splitter.split_documents([doc])

                    # Step 3：创建 Embedding（用 Ollama 本地模型）
                    embeddings = OllamaEmbeddings(
                        model="qllama/bge-small-zh-v1.5:q4_k_m"
                    )

                    # Step 4：构建向量数据库
                    vector_db = FAISS.from_documents(chunks, embeddings)

                    # Step 5：存入 session_state
                    st.session_state.vector_db = vector_db

                    # Step 6：保存到磁盘（持久化）
                    vector_db.save_local(str(KB_DIR / "faiss_index"))
                    meta = {
                        "doc_name": st.session_state.doc_name,
                        "content": st.session_state.uploaded_content,
                        "model": "qllama/bge-small-zh-v1.5:q4_k_m",
                        "chunks": len(chunks),
                        "chunk_size": chunk_size
                    }
                    with open(KB_DIR / "meta.json", "w", encoding="utf-8") as f:
                        json.dump(meta, f, ensure_ascii=False, indent=2)

                    st.success(f"✅ 知识库构建完成！\n共 {len(chunks)} 个文档片段\n💾 已自动保存到本地")

                except Exception as e:
                    st.error(f"❌ 构建失败：{e}")
                    st.info("请确认 Ollama 正在运行：ollama list")

    # 知识库状态显示
    if st.session_state.vector_db is not None:
        st.info(f"📦 知识库已就绪（{st.session_state.vector_db.index.ntotal} 个向量）")
        st.caption(f"📄 文档：{st.session_state.doc_name}")
    else:
        st.warning("⚠️ 知识库未构建")

    # 手动删除知识库按钮
    if st.session_state.vector_db is not None:
        if st.button("🗑️ 删除知识库（重新上传文档）", use_container_width=True):
            st.session_state.vector_db = None
            st.session_state.uploaded_content = ""
            st.session_state.doc_name = ""
            # 删除磁盘文件
            import shutil
            if (KB_DIR / "faiss_index").exists():
                shutil.rmtree(KB_DIR / "faiss_index")
            if (KB_DIR / "meta.json").exists():
                (KB_DIR / "meta.json").unlink()
            st.rerun()

    # 清空对话按钮
    st.markdown("---")
    if st.button("🗑️ 清空对话历史", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ================================================================
# 第四部分：主区域 — 聊天界面
# ================================================================

# 标题区
st.title("💬 知识库问答")

# 知识库状态提示
if st.session_state.vector_db is None:
    st.warning("👈 请先在左侧边栏上传文档并构建知识库")
else:
    st.caption(f"📦 知识库：{st.session_state.doc_name} | top_k={top_k} | temperature={temperature}")

# ----- 显示历史消息 -----
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # 如果有引用来源，显示出来
        if "sources" in msg and msg["sources"]:
            with st.expander("📖 查看引用来源"):
                for i, src in enumerate(msg["sources"], 1):
                    st.markdown(f"**片段 {i}：**")
                    st.code(src, language=None)

# ----- 用户输入 -----
if prompt := st.chat_input("输入你的问题..."):
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 检查知识库是否已构建
    if st.session_state.vector_db is None:
        error_msg = "⚠️ 请先在左侧边栏上传文档并构建知识库！"
        with st.chat_message("assistant"):
            st.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
    elif not api_key:
        error_msg = "⚠️ 请先在左侧边栏输入 Kimi API Key！"
        with st.chat_message("assistant"):
            st.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
    else:
        # ===== 构建 RAG 链 =====
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            try:
                # Step 1：检索最相关的文档片段
                retriever = st.session_state.vector_db.as_retriever(
                    search_kwargs={"k": top_k}
                )
                retrieved_docs = retriever.invoke(prompt)

                # 提取检索到的文本
                context_text = "\n\n---\n\n".join(
                    [doc.page_content for doc in retrieved_docs]
                )

                # Step 2：构建 Prompt
                rag_prompt = ChatPromptTemplate.from_messages([
                    ("system", """你是一个知识库问答助手。请严格根据以下文档内容回答用户的问题。

规则：
1. 只能根据提供的文档内容回答
2. 如果文档中没有相关信息，请回答："根据文档内容，我无法回答这个问题。"
3. 回答要准确、简洁
4. 不要编造文档中没有的信息

文档内容：
{context}"""),
                    ("human", "{question}")
                ])

                # Step 3：创建 LLM
                llm = ChatOpenAI(
                    model="moonshot-v1-8k",
                    api_key=api_key,
                    base_url="https://api.moonshot.cn/v1",
                    temperature=temperature,
                    stream=True  # 开启流式
                )

                # Step 4：手动实现流式 RAG
                # 先构建完整的 prompt
                filled_prompt = rag_prompt.format_messages(
                    context=context_text,
                    question=prompt
                )

                # 流式调用 LLM
                response_stream = llm.stream(filled_prompt)

                # 逐 chunk 渲染
                for chunk in response_stream:
                    if chunk.content:
                        full_response += chunk.content
                        message_placeholder.markdown(full_response + "▌")

                # 去掉光标
                message_placeholder.markdown(full_response)

            except Exception as e:
                full_response = f"❌ 出错了：{e}"
                message_placeholder.error(full_response)

            # 保存 AI 回复到历史
            sources = [doc.page_content[:200] + "..." for doc in retrieved_docs] if st.session_state.vector_db else []
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "sources": sources  # 保存引用来源
            })

# ================================================================
# 第五部分：底部信息
# ================================================================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🛠️ Day 11 | Streamlit 进阶")
with col2:
    st.caption("📚 RAG + FAISS + Kimi")
with col3:
    st.caption("🤖 180天AI工程师路线图")
