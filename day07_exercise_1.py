import os
from openai import OpenAI

class MultiTurnChat:
    def __init__(self, system_prompt="你是一个友好的AI助手。", model="moonshot-v1-8k"):
        """
        初始化多轮对话。
        - 创建 OpenAI client（使用 Moonshot API）
        - 初始化对话历史，包含 system 消息
        - 保存 model 和 client 为实例属性
        """
        self.client = OpenAI(
            api_key=os.environ.get("MOONSHOT_API_KEY", ""),
            base_url="https://api.moonshot.cn/v1"
        )

        self.model = model
        self.history = [{"role": "system", "content": system_prompt}]

    def send_message(self, message):
        """
        发送一条用户消息，获取 AI 回复。
        1. 把用户消息追加到对话历史
        2. 调用 API（传入完整对话历史）
        3. 把 AI 回复也追加到对话历史
        4. 返回 AI 的回复文本
        """
        self.history.append({"role": "user", "content": message})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            temperature=0.9,
            top_p=0.7,
            max_tokens=1024,
            stream=False,
        )
        self.history.append({"role": "assistant", "content": response.choices[0].message.content})
        return response.choices[0].message.content

    def get_history(self):
        """返回当前对话历史（不包含 system 消息）"""
        return [msg for msg in self.history if msg["role"] != "system"]

    def clear_history(self):
        """清空对话历史，只保留 system 消息"""
        self.history = [msg for msg in self.history if msg["role"] == "system"]

    def save_history(self, filename):
        """将对话历史保存到文件"""
        with open(filename, "w", encoding="utf-8") as f:
            for msg in self.get_history():
                f.write(f"{msg['role']}: {msg['content']}\n")

    def load_history(self, filename):
        """从文件加载对话历史"""
        system_msg = [msg for msg in self.history if msg["role"] == "system"]
        with open(filename, "r", encoding="utf-8") as f:
            self.history = []
            for line in f:
                role, content = line.strip().split(": ", 1)
                self.history.append({"role": role, "content": content})
        self.history = system_msg + self.history

    # 测试
chat = MultiTurnChat()
print(chat.send_message("你好，我叫 Root"))
print(chat.send_message("我叫什么名字？"))    # 应该能回答出 Root
print(f"对话轮数：{len(chat.get_history())}")  # 应该是 4（2轮 × user+assistant）
chat.clear_history()
print(f"清空后轮数：{len(chat.get_history())}")  # 应该是 0
