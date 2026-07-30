import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
# 1. 模型
llm = ChatOpenAI(
    model="moonshot-v1-8k",
    api_key=os.environ.get("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1",
)

# 2. prompt（注意 MessagesPlaceholder 放历史消息）
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个友好的助手。"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

# 3. 基础链
chain = prompt | llm | StrOutputParser()

# 4. 用一个字典存所有会话的历史
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    # 提示：如果 session_id 不在 store 里，创建一个 InMemoryChatMessageHistory
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    # 然后返回对应的历史对象
    return store[session_id]
    

# 5. 包一层带记忆的
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",       # 用户输入在哪个字段
    history_messages_key="history",   # 历史消息塞到 prompt 的哪个占位符
)

# 6. 测试：3 轮对话，同一个 session_id
response1 = chain_with_history.invoke(
    {"input": "我叫张三，今年25岁。"},
    config={"configurable": {"session_id": "test_session_1"}}
)
print("AI:", response1)

response2 = chain_with_history.invoke(
    {"input": "我喜欢编程和打篮球。"},
    config={"configurable": {"session_id": "test_session_1"}}
)
print("AI:", response2)

response3 = chain_with_history.invoke(
    {"input": "我叫什么名字？我喜欢什么？"},
    config={"configurable": {"session_id": "test_session_1"}}
)
print("AI:", response3)