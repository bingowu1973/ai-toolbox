# llm.py
import os
import json
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1"
)

def call_llm(prompt, model="moonshot-v1-8k", temperature=0, max_retries=2):
    """
    调用大模型的通用函数
    - prompt: 提示词
    - temperature: 0=稳定输出，越高越随机
    - max_retries: 失败重试次数
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️ 第{attempt+1}次调用失败：{e}")
            if attempt == max_retries - 1:
                return None

def call_llm_json(prompt, **kwargs):
    """
    调用大模型并解析 JSON 输出
    自动处理 ```json ... ``` 包裹的情况
    """
    raw = call_llm(prompt, **kwargs)
    if not raw:
        return None

    # 清理可能的多余格式
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("⚠️ JSON 解析失败，模型输出：")
        print(raw)
        return None