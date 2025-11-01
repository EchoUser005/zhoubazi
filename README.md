# 周运势 AI 分析

这是一个基于 AI 的周运势分析工具。特色：
1. 不同于通用运势分析，本工具根据当日的五行能量结合用户自身属性生成专属的分析报告；
2. 采用专业的天文历法库来精确计算时间信息，为大语言模型（LLM）构建精确、丰富的上下文，规避AI幻觉；
3. 纯私有化使用，降低数据隐私风险；
4. 分析精准，真太阳时自动校准。

![项目截图](example.png)

## 先决条件

在开始之前，请确保开发环境中安装了以下软件：

- [Python](https://www.python.org/downloads/) (版本 3.12 或更高)
- [Node.js](https://nodejs.org/) (版本 18.0 或更高) 和 npm

## 安装与配置

### 1. 克隆代码库

```bash
git clone https://github.com/EchoUser005/zhoubazi
cd zhoubazi
```

### 2. 配置环境变量

复制 `.env.example` 文件为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API 密钥：

```env
# 选择 LLM 提供商 (deepseek 或 gemini)
LLM_PROVIDER=gemini

# DeepSeek API 密钥
DEEPSEEK_API_KEY=sk-your-deepseek-api-key

# Google Gemini API 密钥
GEMINI_API_KEY=your-google-api-key
```

**如何获取 API 密钥：**

- **DeepSeek**: 访问 [DeepSeek 官网](https://platform.deepseek.com/) 注册后获取
- **Google Gemini**: 访问 [Google AI Studio](https://aistudio.google.com/api-keys)，点击"Create API Key"即可获取免费密钥

### 3. 安装 Python 依赖

```bash
# 创建虚拟环境 (可选但推荐)
python -m venv venv

# 激活虚拟环境
# macOS/Linux
source venv/bin/activate
# Windows
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 安装前端依赖

```bash
cd app
npm install
cd ..
```

## 运行项目

```bash
python -m run
```

打开浏览器访问 http://localhost:3000 即可使用应用。

## 注意事项

1. **免责声明：** 本项目的所有输出内容仅供娱乐和技术探讨，不构成任何形式的专业建议。请勿将分析结果作为您做出重要决策的依据。

2. **数据隐私：** 您的个人信息（如生日、城市）仅用于构建API请求，历史记录保存在您的浏览器本地。但请注意，您的数据将会被发送至您自己配置的 DeepSeek 或 Google 服务。

3. **内容准确性：** 命理分析本身并非精确科学，且AI模型的回答具有不确定性，因此分析结果可能存在偏差，请理性看待。