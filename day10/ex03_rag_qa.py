import os
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings  # ← 改这里
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# ============ 1. 准备文档 ============
texts = [
    """LangChain 是一个用于开发大语言模型应用的开源框架。它提供了一系列工具和组件，
帮助开发者快速构建基于 LLM 的应用，比如聊天机器人、问答系统、文本摘要等。
LangChain 的核心概念包括链（Chain）、提示词模板（Prompt Template）、
输出解析器（Output Parser）、工具（Tool）和智能体（Agent）。
它支持多种大模型提供商，如 OpenAI、Anthropic、Moonshot 等，
并且可以通过 LCEL（LangChain Expression Language）用管道符 | 灵活拼接各种组件。""",

    """Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年发布。
Python 以简洁易读的语法著称，强调代码的可读性和简洁性，
因此成为初学者入门编程的首选语言。Python 拥有丰富的标准库和第三方生态，
广泛应用于 Web 开发、数据分析、人工智能、科学计算、自动化运维等领域。
在 AI 和机器学习领域，Python 是事实上的标准语言，
TensorFlow、PyTorch、LangChain 等主流框架都基于 Python 开发。""",

    """机器学习是人工智能的一个分支，它让计算机能够从数据中自动学习和改进，
而不需要被显式编程。机器学习的核心是算法，常见的类型包括监督学习、
无监督学习和强化学习。监督学习需要标注数据，用于分类和回归任务；
无监督学习则从无标签数据中发现模式，比如聚类和降维；
强化学习通过与环境交互获得奖励来优化策略。深度学习是机器学习的一个子领域，
使用多层神经网络来处理复杂问题，在图像识别、自然语言处理等领域取得了突破性进展。""",

    """向量数据库是专门用于存储和检索向量（embedding）的数据库。
与传统数据库存储结构化数据不同，向量数据库存储的是高维向量，
并通过相似度搜索（如余弦相似度）来找到最相近的向量。
常见的向量数据库包括 FAISS、Chroma、Pinecone、Milvus 等。
FAISS 是 Meta 开源的向量检索库，轻量高效，适合本地开发和小规模应用；
Pinecone 和 Milvus 则是分布式向量数据库，适合大规模生产环境。
向量数据库是 RAG（检索增强生成）系统的核心组件之一。""",
]

docs = [Document(page_content=t.strip()) for t in texts]
print(f"准备了 {len(docs)} 篇文档")

# ============ 2. 用 Ollama 本地 embedding 建 FAISS 库 ============
print("正在加载 Ollama embedding 模型...")
embeddings = OllamaEmbeddings(
    model="qllama/bge-small-zh-v1.5:q4_k_m",
    base_url="http://localhost:11434",
)

db = FAISS.from_documents(docs, embeddings)
print(f"✅ 向量库建好啦，共有 {db.index.ntotal} 条向量")

# 检索测试
print("\n--- 检索测试：搜索'向量数据库' ---")
results = db.similarity_search("向量数据库是什么？", k=2)
for i, r in enumerate(results):
    print(f"第 {i+1} 条：{r.page_content[:60]}...")

# ============ 3. 搭 RAG 链 ============
retriever = db.as_retriever(search_kwargs={"k": 2})

prompt = ChatPromptTemplate.from_template("""
你是一个问答助手。请根据以下上下文来回答问题。
如果上下文里没有答案，就说"我不知道"，不要编造。

上下文：
{context}

问题：{question}
""")

llm = ChatOpenAI(
    model="moonshot-v1-8k",
    api_key=os.environ.get("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1",
    temperature=0,
)

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# ============ 4. 测试问答 ============
print("\n" + "="*50)

answer1 = rag_chain.invoke("LangChain 的核心概念有哪些？")
print("问：LangChain 的核心概念有哪些？")
print("答：", answer1)

print("\n" + "="*50)

answer2 = rag_chain.invoke("FAISS 是什么？")
print("问：FAISS 是什么？")
print("答：", answer2)

print("\n" + "="*50)

answer3 = rag_chain.invoke("北京明天的天气怎么样？")
print("问：北京明天的天气怎么样？")
print("答：", answer3)