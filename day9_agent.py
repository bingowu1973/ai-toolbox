import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

# 1. 工具不变
@tool
def calculator(expression: str) -> str:
    """执行数学计算，输入是数学表达式字符串，比如 '3 * 4 + 5'"""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"

@tool
def get_current_time() -> str:
    """获取当前日期和时间"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

tools = [calculator, get_current_time]

# 2. 模型
llm = ChatOpenAI(
    model="moonshot-v1-8k",
    api_key=os.environ.get("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1",
)

# 3. 新版正确创建：用system_prompt传系统词，不要ChatPromptTemplate
executor = create_agent(
    llm,
    tools,
    system_prompt="你是一个聪明的助手，可以使用工具来帮助回答问题。如果问题需要计算或获取时间，请调用相应的工具。"
)

# 4. 调用必须用messages传用户问题，不再用input
result = executor.invoke({
    "messages": [HumanMessage(content="12345 * 67890 等于多少？")]
})
print("测试1:", result["messages"][-1].content)

# 测试2：需要调用时间工具
result2 = executor.invoke({
    "messages": [HumanMessage(content="现在几点了？")]
})
print("测试2:", result2["messages"][-1].content)

# 测试3：不需要工具，直接回答
result3 = executor.invoke({
    "messages": [HumanMessage(content="用一句话解释什么是机器学习")]
})
print("测试3:", result3["messages"][-1].content)