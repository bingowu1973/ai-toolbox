# main.py
import argparse
import json
from llm import call_llm, call_llm_json

def summarize(text):
    """摘要模式：3句话总结"""
    prompt = f"请用3句话总结以下内容，每句话不超过50字：\n\n{text}"
    result = call_llm(prompt)
    return result or "摘要生成失败"

def extract(text):
    """提取模式：从文本中提取结构化信息"""
    prompt = f"""从以下文本中提取信息，严格按JSON格式输出：

文本：{text}

输出格式：
{{
    "names": ["人名1", "人名2"],
    "dates": ["日期1", "日期2"],
    "amounts": ["金额1", "金额2"],
    "locations": ["地点1", "地点2"],
    "key_events": ["事件1", "事件2"]
}}

如果某项信息不存在，值设为空列表 []。
只输出JSON，不要其他内容。"""
    result = call_llm_json(prompt)
    if result:
        return json.dumps(result, ensure_ascii=False, indent=2)
    return "信息提取失败"

def rewrite(text, style="商务正式"):
    """改写模式：按指定风格改写"""
    prompt = f"请将以下文本改写为【{style}】风格，保持核心信息不变：\n\n{text}"
    result = call_llm(prompt, temperature=0.7)  # 改写时稍高温度更有创意
    return result or "改写失败"

def translate(text, target_lang="英文"):
    """翻译模式：翻译成指定语言"""
    prompt = f"请将以下文本翻译成【{target_lang}】：\n\n{text}"
    result = call_llm(prompt)
    return result or "翻译失败"

def main():
    parser = argparse.ArgumentParser(description="🛠️ AI 文本工具箱")
    parser.add_argument("--mode", type=str, required=True,
                       choices=["summary", "extract", "rewrite","translate"],
                       help="处理模式：summary=摘要, extract=提取, rewrite=改写, translate=翻译")
    parser.add_argument("--text", type=str, help="直接输入文本")
    parser.add_argument("--file", type=str, help="从文件读取文本")
    parser.add_argument("--style", type=str, default="商务正式",
                       help="改写风格（仅rewrite模式，默认：商务正式）")
    parser.add_argument("--target_lang", type=str, default="英文",
                       help="翻译目标语言（仅translate模式，默认：英文）")

    args = parser.parse_args()

    # 获取文本
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        print("❌ 请提供 --text 或 --file 参数")
        return

    # 执行对应模式
    print(f"\n🔧 模式：{args.mode}")
    print("=" * 50)

    if args.mode == "summary":
        result = summarize(text)
    elif args.mode == "extract":
        result = extract(text)
    elif args.mode == "rewrite":
        result = rewrite(text, args.style)
    elif args.mode == "translate":
        result = translate(text, args.target_lang)
    print(result)
    print("=" * 50)

if __name__ == "__main__":
    main()