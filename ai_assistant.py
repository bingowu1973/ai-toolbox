import json
from datetime import datetime
from llm import call_llm_tools

#构建计算器函数 calculator(expression)
#输入：数学表达式字符串，如 "123 + 456"
#输出：JSON 字符串，包含 result 或 error
#安全要求：用白名单 + 清 builtins
def calculator(expression):
    # 白名单，只允许特定的函数和操作符
    allowed_names = {
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "len": len  # 支持 +, -, *, /, ** 等基本运算符
    }
    
    # 清理 builtins
    # 原代码试图通过删除 globals() 来清理 builtins，但这会导致 json 等必要模块被删除，
    # 且 eval 的第三个参数 {"__builtins__": {}} 已经实现了安全隔离，因此无需此操作。
    # for name in list(globals().keys()):
    #     if name in allowed_names:
    #         continue
    #     del globals()[name]

    try:
        # 使用 eval 执行表达式，但只允许白名单中的函数
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})

#2. 天气查询 get_weather(city)
#输入：城市名
#输出：JSON 字符串，包含 temp、condition、humidity 等
#用模拟数据就行（北京/上海/深圳... 写死几个城市）
#3. 时间查询 get_current_time()
#输入：不需要参数（或者 timezone 可选）
#输出：JSON 字符串，包含 time（年月日时分秒）和 weekday（星期几）
def get_weather(city):
    weather_data = {
        "北京": {"temp": 28, "condition": "晴", "humidity": 45},
        "上海": {"temp": 32, "condition": "多云", "humidity": 65},
        "深圳": {"temp": 34, "condition": "雷阵雨", "humidity": 85},
        "杭州": {"temp": 30, "condition": "小雨", "humidity": 78},
    }
    data = weather_data.get(city)
    if data:
        return json.dumps({"city": city, **data}, ensure_ascii=False)
    else:
        return json.dumps({"error": f"不支持的城市：{city}"}, ensure_ascii=False)

def get_current_time():
    now = datetime.now()
    weekday_map = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return json.dumps({
        "time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "weekday": weekday_map[now.weekday()]
    }, ensure_ascii=False) 
 
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "执行数学计算,支持基本运算和部分内置函数，如 abs、round、min、max 等。当需要精确计算数值时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式,如 '123 + 456' 或 'abs(-5) + round(3.14)'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气信息,包括温度、天气状况和湿度。当用户问天气时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，如北京、上海、深圳"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期、时间和星期几。当用户问现在几点、今天几号、星期几等问题时使用。",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


def run_assistant(messages, available_functions, max_steps=5):
    for step in range(max_steps):
        # ① 调用 API
        result = call_llm_tools(messages, tools, tool_choice="auto")
        
        # ② 如果没有 tool_calls，说明回答完了
        if not result["tool_calls"]:
            return result["content"]
        
        # ③ 构造标准格式的 assistant 消息，加入历史
        assistant_message = {
            "role": "assistant",
            "content": result["content"],
            "tool_calls": [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": json.dumps(tc["arguments"], ensure_ascii=False)
                    }
                }
                for tc in result["tool_calls"]
            ]
        }
        messages.append(assistant_message)
        
        # ④ 遍历执行每个工具调用
        for tool_call in result["tool_calls"]:
            tool_name = tool_call["name"]
            tool_args = tool_call["arguments"]  # 已经是 dict 了
            
            if tool_name in available_functions:
                print(f"🔧 调用 {tool_name}({tool_args})")
                function_result = available_functions[tool_name](**tool_args)
            else:
                function_result = json.dumps({"error": f"未知函数: {tool_name}"})
            
            # ⑤ 把工具结果加入消息（四个字段都要有）
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": tool_name,
                "content": str(function_result)
            })
    
    return "抱歉，处理步骤太多了。"

def main():
    """主循环：命令行交互"""
    print("=" * 50)
    print("🤖 AI 智能助理（带工具版）")
    print("   输入内容开始对话，输入 quit 退出")
    print("   输入 tools 查看可用工具")
    print("=" * 50)
    
    messages = []  # 维护完整对话历史
    
    available_functions = {
        "calculator": calculator,
        "get_weather": get_weather,
        "get_current_time": get_current_time,
    }
    
    while True:
        # ① 读取用户输入
        user_input = input("\n你: ")
        
        # ② 处理特殊命令
        if user_input.lower() == "quit":
            print("👋 再见！")
            break
        
        if user_input.lower() == "tools":
            print("\n📋 可用工具：")
            for name, func in available_functions.items():
                print(f"   - {name}: {func.__doc__ or '无描述'}")
            continue
        
        # ③ 普通对话：加入历史 → 跑助理 → 输出回答
        messages.append({"role": "user", "content": user_input})
        
        answer = run_assistant(messages, available_functions)
        
        messages.append({"role": "assistant", "content": answer})
        print(f"\n🤖 助理: {answer}")

if __name__ == "__main__":
    main()    

