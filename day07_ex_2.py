import json
import re
def safe_parse_json(text):
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
        end = text.find('```', start + 7)
        if start != -1 and end != -1:
            start = text.find('{', start, end)
            end = text.rfind('}', start, end)
            if start != -1 and end != -1:   
                return json.loads(text[start:end+1].strip())
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

    # 5. 以上都失败 → 抛出 ValueError
    raise ValueError("无法解析 JSON 对象")         

# 测试用例
# 情况1：纯 JSON
assert safe_parse_json('{"name": "Root", "age": 25}') == {"name": "Root", "age": 25}

# 情况2：代码块包裹
assert safe_parse_json('```json\n{"name": "Root"}\n```') == {"name": "Root"}

# 情况3：前后有文字
assert safe_parse_json('好的，结果如下：\n{"name": "Root"}\n希望对你有帮助！') == {"name": "Root"}

# 情况4：尾随逗号
assert safe_parse_json('{"name": "Root", "age": 25,}') == {"name": "Root", "age": 25}

# 情况5：无法解析
try:
    safe_parse_json("这不是 JSON")
    assert False, "应该抛出 ValueError"
except ValueError:
    pass

print("✅ 所有测试通过！")

