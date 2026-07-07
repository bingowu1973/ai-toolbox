def trim_conversation(history, max_turns=5):
    """
    截断对话历史，保留 system 消息和最近的 max_turns 轮对话。
    
    参数：
        history: 对话历史列表，格式为 [{"role": ..., "content": ...}, ...]
        max_turns: 最多保留的对话轮数（一轮 = 一条 user + 一条 assistant）
    返回：
        截断后的对话历史列表
    
    规则：
    - 始终保留第一条 system 消息
    - 保留最近的 max_turns 轮对话（即最后 max_turns*2 条 user/assistant 消息）
    - 如果总消息数 <= 1 + max_turns*2，不做截断
    """
    system_msg = None
    if history and history[0].get("role") == "system":
        system_msg = history[0]
        non_system_history = history[1:]
    else:
        non_system_history = history
    
    if len(non_system_history) <= max_turns * 2:
        return history
    
    trimmed_non_system = non_system_history[-(max_turns * 2):]
    
    if system_msg:
        return [system_msg] + trimmed_non_system
    else:
        return trimmed_non_system
    
# 测试
history = [{"role": "system", "content": "你是助手"}]
for i in range(10):
    history.append({"role": "user", "content": f"问题{i}"})
    history.append({"role": "assistant", "content": f"回答{i}"})

# 原始长度：1 + 20 = 21
print(f"截断前：{len(history)} 条消息")

trimmed = trim_conversation(history, max_turns=3)
print(f"截断后：{len(trimmed)} 条消息")  # 应该是 1 + 6 = 7

# 验证：第一条仍是 system
assert trimmed[0]["role"] == "system"
# 验证：保留的是最后3轮（问题7/8/9）
assert trimmed[1]["content"] == "问题7"
assert trimmed[-1]["content"] == "回答9"
print("✅ 截断测试通过！")