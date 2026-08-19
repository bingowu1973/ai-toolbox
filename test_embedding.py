#import os
#from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5",
    model_kwargs={"device": "cpu"}
)

# FAISS.from_documents(splits, embeddings) 代码完全不用改



# 简单测单个文本向量化
vec = embeddings.embed_query("测试Moonshot向量接口")
print(f"向量维度：{len(vec)}")
