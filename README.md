🛠️ AI 文本工具箱

一个基于大语言模型的命令行文本处理工具，支持摘要、信息提取、风格改写。

功能

摘要 — 输入长文，输出3句话总结
提取 — 从文本中提取人名、日期、金额等结构化信息（JSON格式）
改写 — 按指定风格改写文本（商务正式、轻松口语等）

安装

1. 克隆项目

bash
# 把代码从 GitHub 下载到本地
git clone https://github.com/bingowu1973/ai-toolbox.git

# 进入项目目录
cd ai-toolbox


2. 创建虚拟环境

bash
python -m venv venv

# Mac/Linux 激活
source venv/bin/activate

# Windows 激活
.\venv\Scripts\activate


3. 安装依赖

bash
pip install -r requirements.txt


如果 pip 下载慢，先换国内镜像：

bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple


使用

摘要模式

bash
python main.py --mode summary --file sample.txt


输出示例：

plaintext
🔧 模式：summary
==================================================
1. 2026年5月20日，全球人工智能大会在北京举行。
2. 星辰科技发布了"星语3.0"模型，参数量5000亿，训练成本2.3亿美元。
3. 下届大会将于11月在深圳举办，预计参会超5万人。
==================================================


信息提取模式

bash
python main.py --mode extract --file sample.txt


输出示例：

json
{
  "names": ["张三", "李四", "王五"],
  "dates": ["2026年5月20日", "2026年11月"],
  "amounts": ["2.3亿美元", "0.5%", "5万人"],
  "locations": ["北京", "深圳"],
  "key_events": ["星语3.0发布", "AI安全治理讨论", "下届大会宣布"]
}


风格改写模式

bash
# 默认商务正式风格
python main.py --mode rewrite --file sample.txt

# 指定其他风格
python main.py --mode rewrite --file sample.txt --style "轻松口语"
python main.py --mode rewrite --file sample.txt --style "新闻报道"


直接输入文本（不用文件）

bash
python main.py --mode summary --text "今天天气真好，适合出门散步"


保存结果到文件

bash
# 加 --output 参数，结果会保存到指定文件
python main.py --mode extract --file sample.txt --output result.json


参数说明

表格
参数	说明	默认值	可选值
--mode	处理模式（必填）	无	summary / extract / rewrite
--text	直接输入文本	无	任意字符串
--file	从文件读取文本	无	文件路径
--style	改写风格	商务正式	任意风格描述
--output	结果保存到文件	无	文件路径

--text 和 --file 二选一，必须提供其中一个。

## 网页版使用

```bash
streamlit run app.py

配置

本项目使用 Kimi API（兼容 OpenAI 格式），需要配置 API Key。

获取 API Key

访问 Kimi 开放平台 注册账号
进入 API Key 管理页面，创建一个新的 Key
复制 Key（以 sk- 开头的字符串）

设置环境变量

Mac / Linux：

bash
# 临时设置（当前终端窗口有效）
export MOONSHOT_API_KEY="sk-你的key"

# 永久设置（写入配置文件，每次打开终端自动生效）
echo 'export MOONSHOT_API_KEY="sk-你的key"' >> ~/.bashrc
source ~/.bashrc


Windows（PowerShell）：

powershell
# 永久设置
[System.Environment]::SetEnvironmentVariable("MOONSHOT_API_KEY", "sk-你的key", "User")


⚠️ 设置环境变量后需要重启 VS Code 终端才能生效。

⚠️ 永远不要把 API Key 硬编码在代码里或推到 GitHub！ 项目已通过 .gitignore 排除了 .env 文件。

项目结构

plaintext
ai-toolbox/
├── main.py            # 主程序：命令行参数 + 业务函数
├── llm.py             # LLM 封装：call_llm() + call_llm_json()
├── sample.txt         # 示例测试文本
├── requirements.txt   # 项目依赖列表
├── .gitignore         # Git 忽略文件（venv、.env等）
└── README.md          # 本文件


技术栈

Python 3.11+ — 编程语言
Kimi API — 大语言模型接口（兼容 OpenAI 格式）
argparse — Python 自带命令行参数解析
json — 结构化数据输入输出

许可

MIT License — 可自由使用、修改和分发。