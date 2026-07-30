import os
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# ============ 1. 准备文档 ============
texts = [
    "LangChain 是一个用于开发大语言模型应用的开源框架。它提供了一套标准化的接口和工具，使得开发者能够轻松地将大语言模型与其他数据源、计算资源以及外部API进行集成。LangChain 的核心组件包括模型输入输出管理、数据连接、链式调用、记忆模块以及代理系统等。通过这些组件，开发者可以构建出诸如文档问答、聊天机器人、数据提取和代码分析等复杂的AI应用。此外，LangChain 支持多种主流大模型，并具备极高的可扩展性，极大地降低了AI应用的开发门槛。",
    "Python 是一种广泛使用的高级编程语言，以其简洁明了的语法和强大的标准库而闻名。它支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。Python 的设计哲学强调代码的可读性和简洁性，尤其是使用空格缩进来划分代码块，这使得开发者能够用更少的代码行来表达复杂的逻辑。Python 在数据科学、人工智能、网络开发、自动化脚本等领域有着广泛的应用，拥有庞大的社区和丰富的第三方库，如 NumPy、Pandas 和 TensorFlow，极大地提升了开发效率。",
    "机器学习是人工智能的一个重要分支，它使计算机系统能够从数据中学习并改进其性能，而无需进行明确的编程。机器学习的核心在于构建和分析算法，这些算法能够从历史数据中学习模式，并对新的、未见过的数据做出预测或决策。常见的机器学习任务包括分类、回归、聚类和降维等。根据学习方式的不同，机器学习可以分为监督学习、无监督学习和强化学习。随着大数据和计算能力的飞速发展，机器学习已经在图像识别、语音处理、推荐系统和医疗诊断等领域取得了突破性的成果。",
    "深度学习是机器学习的一个子领域，它基于人工神经网络的研究，特别是具有多个隐藏层的深度神经网络。深度学习通过多层非线性变换，能够自动地从原始数据中提取高层次的特征，这被称为特征学习。相比于传统的机器学习方法需要人工设计特征，深度学习在处理图像、声音和文本等非结构化数据时展现出了极大的优势。卷积神经网络（CNN）和循环神经网络（RNN）是两种经典的深度学习模型，它们在计算机视觉和自然语言处理等任务中取得了前所未有的成功。",
    "自然语言处理（NLP）是计算机科学与人工智能交叉领域的一个重要方向，旨在让计算机理解、解释和生成人类语言。NLP 的应用非常广泛，包括机器翻译、情感分析、文本摘要、问答系统和对话系统等。近年来，随着 Transformer 架构的提出和预训练语言模型（如 BERT、GPT 系列）的兴起，NLP 领域取得了革命性的进展。这些大语言模型通过在海量文本数据上进行无监督预训练，学习到了丰富的语言知识，从而在各类下游任务中展现出卓越的泛化能力。"
]

# 转成 Document 对象
docs = [Document(page_content=t) for t in texts]

# 切分（可选，因为我们的文档本身不长，也可以不切直接用）
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
splits = text_splitter.split_documents(docs)

# ============ 2. 建向量库 ============
embeddings = OllamaEmbeddings(model="nomic-embed-text")
 
# 用 FAISS 建向量库
db = FAISS.from_documents(splits, embeddings)   # 如果切了就用 splits
print(f"向量库建好啦，共有 {db.index.ntotal} 条向量")

# ============ 3. 搭 RAG 链 ============
retriever = db.as_retriever(search_kwargs={"k": 2})  # 每次最多返回 2 个相关文档

prompt = ChatPromptTemplate.from_template("""
你是一个问答助手。请根据以下上下文来回答问题。
如果上下文里没有答案，就说"我不知道"，不要编造。

上下文：
{context}

问题：{question}
""")
# 检查环境变量
MOONSHOT_API_KEY = os.environ.get("MOONSHOT_API_KEY")
if not MOONSHOT_API_KEY:
    raise ValueError("环境变量 MOONSHOT_API_KEY 未设置，请先设置您的 Moonshot API Key。")

llm = ChatOpenAI(
    model="moonshot-v1-8k",
    api_key=MOONSHOT_API_KEY,
    base_url="https://api.moonshot.cn/v1",
    temperature=0,    # 设为 0，回答更稳定、不瞎编
)

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# ============ 4. 测试 ============
# 问题 1：文档里有的
answer1 = rag_chain.invoke("LangChain 是什么？")
print("问：LangChain 是什么？")
print("答：", answer1)
print()

# 问题 2：文档里没有的
answer2 = rag_chain.invoke("北京今天天气怎么样？")
print("问：北京今天天气怎么样？")
print("答：", answer2)
