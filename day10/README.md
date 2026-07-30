---
AIGC:
    Label: "1"
    ContentProducer: 001191110102MACQD9K64018705
    ProduceID: 7634031641446449444-data_volume/files/所有对话/主对话/day10/README.md
    ReservedCode1: ""
    ContentPropagator: 001191110102MACQD9K64028705
    PropagateID: 2068615131826676#1785418653856
    ReservedCode2: ""
---
# Day 10：LangChain 进阶 — 记忆 + 文档 + Embedding + RAG 入门

## 📌 今日目标
掌握 RAG（检索增强生成）的核心基础：对话记忆、文档切分、Embedding 向量、向量数据库、最简 RAG 系统搭建。

## 📚 核心知识点

### 1. 对话记忆（Memory）
- `RunnableWithMessageHistory`：自动管理对话历史的包装器
- `InMemoryChatMessageHistory`：内存版对话历史存储
- `MessagesPlaceholder`：prompt 中放置历史消息的占位符
- `session_id`：区分不同会话的标识

### 2. 文档加载与切分
- `TextLoader` / 手动读取：加载文本文件为 Document 对象
- `RecursiveCharacterTextSplitter`：递归字符切分器（最常用）
- 关键参数：`chunk_size`（块大小）、`chunk_overlap`（重叠量）、`separators`（切分分隔符优先级）

### 3. Embedding 与向量数据库
- **Embedding**：把文本转成高维向量，语义相近的文本向量距离近
- **向量数据库**：存储向量并支持相似度搜索（FAISS / Chroma / Pinecone 等）
- **相似度搜索**：用余弦相似度找到最相关的文档片段

### 4. RAG（检索增强生成）
- 核心流程：用户提问 → 语义检索相关文档 → 文档+问题塞入 prompt → 模型基于文档回答
- 优势：使用私有数据、降低幻觉、可溯源
- 防幻觉关键：prompt 中明确要求"不知道就说不知道"

## 📁 文件说明

| 文件 | 内容 | 运行依赖 |
|------|------|----------|
| `ex01_memory_chat.py` | 带记忆的对话机器人（3 轮验证） | langchain、langchain-openai |
| `ex02_doc_splitter.py` | 文档切分与 chunk_size 对比实验 | langchain-text-splitters |
| `ex03_rag_qa.py` | 最简 RAG 问答系统 | faiss-cpu、langchain-community、Ollama |

## 🚀 运行方法

### 前置准备
```bash
# 基础依赖
pip install langchain langchain-openai langchain-text-splitters -i https://pypi.tuna.tsinghua.edu.cn/simple

# RAG 相关依赖
pip install faiss-cpu langchain-community -i https://pypi.tuna.tsinghua.edu.cn/simple

# 设置 Kimi API Key
set MOONSHOT_API_KEY=你的key
```

### 运行第 3 题（RAG）的特殊准备
第 3 题使用 Ollama 本地 embedding 模型（Kimi 无公开 embedding API）：

```bash
# 1. 确保 Ollama 已安装并运行
ollama serve

# 2. 拉取中文 embedding 模型
ollama pull qllama/bge-small-zh-v1.5:q4_k_m

# 3. 运行 RAG 脚本
python ex03_rag_qa.py
```

> 💡 备选方案：也可以用 `sentence-transformers` + `BAAI/bge-small-zh-v1.5` 直接在 Python 中加载模型，不需要 Ollama。

## ✅ 练习题完成情况
- [x] 第 1 题：带记忆的对话机器人 → 3 轮对话验证记忆生效
- [x] 第 2 题：文档加载与切分 → 对比 100/200/500 三种 chunk_size 效果
- [x] 第 3 题：最简 RAG 问答系统 → 3 轮问答（2 道能答 + 1 道说不知道）

## 🔗 相关链接
- [LangChain 官方文档](https://python.langchain.com/)
- [FAISS GitHub](https://github.com/facebookresearch/faiss)
- [BAAI/bge-small-zh](https://huggingface.co/BAAI/bge-small-zh-v1.5)
- [Ollama 官网](https://ollama.com/)

---

> 本内容由 Coze AI 生成，请遵循相关法律法规及《人工智能生成合成内容标识办法》使用与传播。
