import json
import re
import sys
from llm import call_llm
from typing import Dict, Any, Optional

# 定义人物档案的JSON schema
PERSON_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "gender": {"type": "string"},
        "occupation": {"type": "string"},
        "address": {"type": "string"},
        "contact": {"type": "string"},
        "education": {"type": "string"},
        "experience": {"type": "string"}
    },
    "required": ["name"]
}

def safe_parse_json(text: str) -> Optional[Dict[str, Any]]:
    """
    从模型回复中安全地提取 JSON 对象。
    
    需要处理以下情况（按优先级尝试）：
    1. 纯 JSON 字符串 → 直接解析
    2. 被 ```json ... ``` 包裹 → 提取代码块内容后解析
    3. JSON 前后有多余文字 → 找到 { 到 } 的部分解析
    4. JSON 中有尾随逗号（如 {"a": 1, "b": 2,}） → 修复后解析
    5. 以上都失败 → 抛出 ValueError
    
    参数：text - 模型返回的原始文本
    返回：解析后的 Python 字典
    异常：如果所有方法都失败，抛出 ValueError
    """

    # 1. 纯 JSON 字符串 → 直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. 被 ```json ... ``` 包裹 → 提取代码块内容后解析
    try:   
        start = text.find('```json')
        if start == -1:
            json_str = text
        else:
            end = text.find('```', start + 7)
            if end != -1:
                json_str = text[start+7:end].strip()
            else:
                json_str = text[start+7:].strip()

            return json.loads(json_str)
    except json.JSONDecodeError:    
        pass
        
    # 3. JSON 前后有多余文字 → 找到 { 到 } 的部分解析
    try:
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            json_str = text[start:end+1]
            # 4. JSON 中有尾随逗号 → 修复后解析
            json_str = re.sub(r",\s*}", "}", json_str)
            json_str = re.sub(r",\s*]", "]", json_str)
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # 5. 以上都失败 → 返回 None
    return None  

def validate_json(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    验证JSON数据是否符合schema要求
    """
    required_fields = schema.get("required", [])
    properties = schema.get("properties", {})
    
    # 检查必填字段是否存在
    for field in required_fields:
        if field not in data:
            return False
    
    # 检查字段类型是否正确
    for field, value in data.items():
        if field in properties:
            expected_type = properties[field]["type"]
            if expected_type == "string" and not isinstance(value, str):
                return False
            elif expected_type == "integer" and not isinstance(value, int):
                return False
    
    return True

def call_kimi_api(text: str, retry_count: int = 0, error_info: str = "") -> Optional[Dict[str, Any]]:
    """
    调用Kimi API提取信息
    """
    if retry_count >= 3:
        return None

    # 构建prompt
    base_prompt = f"""
    请从以下文本中提取人物信息，并按照指定的JSON格式返回：
    {text}
    
    要求返回的JSON格式必须包含以下字段：
    - name: 姓名（字符串）
    - age: 年龄（整数，可选）
    - gender: 性别（字符串，可选）
    - occupation: 职业（字符串，可选）
    - address: 地址（字符串，可选）
    - contact: 联系方式（字符串，可选）
    - education: 教育背景（字符串，可选）
    - experience: 工作经验（字符串，可选）
    """
    
    # 如果是重试，添加更严格的格式要求
    if retry_count > 0:
        base_prompt += f"""
        注意：请严格按照JSON格式返回，不要包含任何其他文本。
        确保所有必填字段都存在且类型正确。
        上次的错误信息：{error_info}
        重新尝试提取信息。
        """

    try:  
        result = call_llm(base_prompt)
        # 模拟API响应
        #result = {"choices": [{"message": {"content": '{"name": "张三", "age": 25, "gender": "男", "occupation": "工程师"}'}}]}
        
        # 提取JSON内容
        json_str = result
         
        parsed_data = safe_parse_json(json_str)
         
        if parsed_data and validate_json(parsed_data, PERSON_SCHEMA):
            return parsed_data
        else:
           # 解析失败时重试，并在 prompt 中附上次的错误信息
            error_info = "解析失败或JSON不符合要求。"
            return call_kimi_api(text, retry_count + 1, error_info=error_info)
            
    except Exception as e:
        print(f"API调用失败: {e}")
        return call_kimi_api(text, retry_count + 1, error_info=str(e))

def main():
    """
    主函数
    """
    # 用 sys.stdin 读取多行输入
    print("请输入要提取信息的文本：")
    text = sys.stdin.read()
    # text = input("请输入要提取信息的文本：")
    
    # 调用API提取信息
    result = call_kimi_api(text)
    
    if result:
        # 输出干净的JSON
        print("\n提取的信息：")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("信息提取失败，请检查输入文本或稍后重试。")

if __name__ == "__main__":
    main()
