
#目标：给一段文章，让模型输出结构化的 JSON 结果（标题、分类、关键词、摘要）。
#背景：以前我们用 prompt + 正则清理来拿 JSON，现在用 LangChain 的 JsonOutputParser，更标准更稳。
#题目
#写一个函数 analyze_article(text)，输入文章内容，输出如下结构的字典：
#python 
#{
#    "title": "一句话标题",
#    "category": "科技/财经/生活/教育/其他",  # 五选一
#    "keywords": ["关键词1", "关键词2", "关键词3"],  # 3个关键词
#    "summary": "50字以内摘要"
#}
#要求：
#用 ChatPromptTemplate 定义 prompt
#用 JsonOutputParser 解析输出
#用 LCEL 管道 | 组装成链
测试至少 2 篇不同类型的文章
 
import os
from typing import List
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# 检查环境变量是否设置
if not os.environ.get("MOONSHOT_API_KEY"):
    raise ValueError("请在环境变量中设置 MOONSHOT_API_KEY")

# 1. 定义模型（注意用Kimi的base_url和api_key）
llm = ChatOpenAI(
    model="moonshot-v1-8k", 
    api_key=os.environ.get("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1",
)
# 2. 定义数据结构
class ArticleInfo(BaseModel):
    title: str = Field(description="一句话标题")
    category: str = Field(description="科技/财经/生活/教育/其他")  # 五选一
    keywords: List[str] = Field(description="3个关键词")    
    summary: str = Field(description="50字以内摘要")

# 3. 定义JsonOutputParser       
json_parser = JsonOutputParser(pydantic_object=ArticleInfo)

# 4. 定义prompt（要包含{format_instructions}），并使用 partial 预注入格式指令
prompt = ChatPromptTemplate.from_template(
    "请根据以下内容生成结构化信息：\n\n{content}\n\n请按照以下格式输出：\n\n{format_instructions}"
).partial(format_instructions=json_parser.get_format_instructions())

# 5. 用 | 拼成链
chain = prompt | llm | json_parser


# 6. 定义 analyze_article 函数
def analyze_article(text):
    result = chain.invoke({"content": text})
    return result

# 7. 测试至少 2 篇不同类型的文章
article_1 = "核心结论： 该课程目前处于“教育情怀产物”阶段，不具备商业可行性。它犯了教育产品商业化的“大忌”——概念虚空、IP错位、交付模糊。若直接投入市场，失败率超过90%。"
article_2 = "苹果公司今日发布了最新的财务报告，显示其服务业务收入创下历史新高，达到200亿美元。尽管硬件销售略有下滑，但整体利润率因服务业务的强劲增长而得到了显著提升。分析师认为，苹果正在成功实现从硬件公司向服务型公司的转型。"

print("文章1分析结果：", analyze_article(article_1))
print("文章2分析结果：", analyze_article(article_2))
