import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
llm = ChatOpenAI(
    model="moonshot-v1-8k",
    api_key=os.environ.get("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1",
)

# 第一步：翻译
translate_prompt = ChatPromptTemplate.from_template(
    "请将以下内容翻译成英文：\n\n{content}"
)
translate_chain = translate_prompt | llm | StrOutputParser()

# 第二步：标题和摘要并联（注意它们的输入变量叫 translated_text）
title_prompt = ChatPromptTemplate.from_template(
    "请为以下内容生成一个5个单词以内的简短的英文标题：\n\n{translated_text}"
)
title_chain = title_prompt | llm | StrOutputParser()

summary_prompt = ChatPromptTemplate.from_template(
    "请为以下内容生成一个15个单词以内的简短的英文摘要：\n\n{translated_text}"
)
summary_chain = summary_prompt | llm | StrOutputParser()

# 把翻译的结果"喂"给并联的两个链
full_chain = {
    "translated_text": translate_chain  # 翻译结果存到 translated_text
} | RunnableParallel({
    "title": title_chain,
    "summary": summary_chain,
})

# 输入中文内容
result = full_chain.invoke({ "content": "核心结论： 该课程目前处于“教育情怀产物”阶段，不具备商业可行性。它犯了教育产品商业化的“大忌”——概念虚空、IP错位、交付模糊。若直接投入市场，失败率超过90%。" })
print(result["title"])
print(result["summary"])

