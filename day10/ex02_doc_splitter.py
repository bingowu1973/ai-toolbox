import tempfile
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. 先创建一个测试文本文件（4段，每段至少100字）
test_content = """
Python是一种广泛使用的高级编程语言。它的设计哲学强调代码的可读性和简洁性，尤其是使用空格缩进划分代码块。相比于C++或Java，Python让开发者能够用更少的代码行表达复杂的逻辑。Python支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。它拥有一个庞大且全面的标准库，涵盖了网络通信、文本处理、数据库接口等各个方面，极大地提升了开发效率。

人工智能是计算机科学的一个重要分支，致力于研究和开发用于模拟、延伸和扩展人类智能的理论与技术。近年来，随着深度学习算法的突破和计算能力的提升，人工智能取得了飞速发展。从自动驾驶汽车到智能语音助手，从医疗影像分析到金融风控预测，AI技术正在深刻地改变着我们的生活方式和生产模式，成为推动社会进步的核心力量之一。

中国饮食文化源远流长，博大精深。由于地域辽阔，气候、物产和风俗的差异，各地形成了独具特色的菜系，如鲁菜、川菜、粤菜、苏菜、闽菜、浙菜、湘菜和徽菜等八大菜系。中国菜肴讲究色、香、味、意、形，不仅注重食材的搭配与烹饪技法的运用，更蕴含着深厚的文化底蕴与哲学思想，是中华民族传统文化的重要组成部分。

宇宙探索是人类永恒的追求。从古代的天文观测到现代的太空探测，人类对宇宙的认知不断深化。随着航天技术的进步，我们不仅成功登陆了月球，还向火星、木星等遥远星球发射了探测器。空间站的建设更是为人类在太空中长期驻留提供了可能。未来，星际旅行和地外生命探索将继续激发人类的想象力，推动科学技术的不断突破。
"""

# 保存到临时文件，程序结束后自动清理，避免污染当前目录
with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as f:
    f.write(test_content)
    temp_file_path = f.name

try:
    # 2. 加载文档
    loader = TextLoader(temp_file_path, encoding="utf-8")
    docs = loader.load()
    print(f"加载了 {len(docs)} 个文档")
    
    if docs:
        print(f"文档总长度：{len(docs[0].page_content)} 字")
    else:
        print("未加载到任何文档内容。")

    # 3. 切分
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=30,
        separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""],
    )
    splits = text_splitter.split_documents(docs)

    # 4. 打印结果
    print(f"\n切分成了 {len(splits)} 块：")
    for i, doc in enumerate(splits):
        preview = doc.page_content[:50].replace("\n", " ")
        print(f"  第 {i+1} 块：[{len(doc.page_content)}字] {preview}...")
finally:
    # 清理临时文件
    import os
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
