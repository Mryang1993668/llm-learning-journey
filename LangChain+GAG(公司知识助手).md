🚀 RAG 实战：基于 LangChain 官方组件的公司知识助手
从 Dify 可视化到代码实现，完整记录基于 LangChain 官方阿里云组件搭建 RAG 应用的实战过程。

📋 项目简介
本项目是一个基于 LangChain 官方阿里云组件 构建的公司内部知识问答助手。它能够读取公司文档（如员工手册），通过 RAG（检索增强生成）技术，准确回答员工关于公司政策、福利、制度等方面的问题。

✨ 核心功能
问题类型	示例	预期行为
````
✅ 知识库内问题	"公司有什么福利？"	基于员工手册准确回答
✅ 知识库内问题	"请假怎么请？"	列出年假、病假、事假政策
❌ 知识库外问题	"你们卖什么产品？"	返回"知识库中未找到"
❌ 无关闲聊	"今天天气怎么样？"	礼貌引导回公司话题
````

🏗️ 技术架构
```text
    用户输入
        ↓
    [TextLoader] 加载文档
        ↓
    [RecursiveCharacterTextSplitter] 文本分块
        ↓
    [DashScopeEmbeddings] 阿里云向量化
        ↓
    [FAISS] 向量库存储
        ↓
    [Retriever] 知识检索 (Top K=3)
        ↓
    [ChatTongyi] LLM 生成回答 (qwen-plus)
        ↓
    [StrOutputParser] 输出解析
        ↓
    最终答案
```
🧩 核心组件
组件	技术选型	说明
开发框架	LangChain 0.2.x	应用开发框架
LLM 模型	qwen-plus	阿里云百炼通义千问
Embedding 模型	text-embedding-v3	阿里云向量化模型
向量数据库	FAISS	本地向量存储
文档加载	TextLoader	支持 txt 格式
文本分块	RecursiveCharacterTextSplitter	块大小 500，重叠 50
🔧 环境配置
1. 硬件环境
项目	配置
操作系统	Windows 10 64位
内存	8GB
Python 版本	3.19
2. 安装依赖
bash
# 安装所需包
pip install langchain-community
pip install langchain-core
pip install langchain-text-splitters
pip install dashscope
pip install python-dotenv
pip install faiss-cpu
3. 环境变量配置
在项目根目录创建 .env 文件：

env
# 阿里云百炼配置
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
⚠️ 注意：请替换为你自己的 API Key，不要硬编码在代码中。

4. 准备测试文档
创建 公司员工手册.txt：

text
# 公司员工手册

## 考勤制度
工作时间：周一至周五 9:00-18:00，午休1小时。
迟到超过30分钟记为半天事假。

## 休假政策
年假：入职满1年享受5天年假，每增加1年增加1天，上限15天。
病假：需提供医院证明，每月可享1天带薪病假。
事假：需提前申请，按天扣除工资。

## 福利待遇
五险一金：全额缴纳，公积金比例12%。
餐补：每天30元，随工资发放。
交通补贴：每月200元。
年度体检：每年一次，公司全额承担。
📝 核心代码
项目文件结构
```text
        llm-learning/
        ├── .env                          # 环境变量配置
        ├── .gitignore                    # Git 忽略文件
        ├── 公司员工手册.txt               # 测试文档
        ├── rag_langchain.py              # 主程序
        ├── faiss_index/                   # 向量库（自动生成）
        │   ├── index.faiss
        │   └── index.pkl
        └── README.md                      # 本文档

```
##关键代码解析
python
# 1. 初始化阿里云组件
llm = ChatTongyi(
    model="qwen-plus",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
    temperature=0.1,
)

embeddings = DashScopeEmbeddings(
    model="text-embedding-v3",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)

# 2. 加载并处理文档
loader = TextLoader("公司员工手册.txt", encoding="utf-8")
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)
docs = text_splitter.split_documents(documents)

# 3. 创建向量库
vectorstore = FAISS.from_documents(docs, embeddings)

# 4. 构建 RAG 链
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
完整代码请查看项目中的 rag_langchain.py。

🧪 运行与测试
启动程序
bash
python rag_langchain.py
测试结果
text
❓ 请输入问题：公司有什么福利？

💡 答案：- 五险一金：全额缴纳，公积金比例12%  
- 餐补：每天30元，随工资发放  
- 交通补贴：每月200元  
- 年度体检：每年一次，公司全额承担

❓ 请输入问题：请假怎么请？

💡 答案：- 事假：需提前申请，按天扣除工资  
- 病假：需提供医院证明，每月可享1天带薪病假  
- 年假：入职满1年可享5天，逐年递增（每满1年+1天，上限15天）

❓ 请输入问题：你们公司卖什么产品？

💡 答案：我是公司内部知识助手，只能回答公司相关的问题哦

❓ 请输入问题：今天天气怎么样？

💡 答案：我是公司内部知识助手，只能回答公司相关的问题哦

✅ 所有测试用例全部通过！


🎯 项目价值
````
技术收获
✅ 掌握 LangChain 0.2.x 的正确使用方式
✅ 学会集成阿里云百炼官方组件
✅ 理解 RAG 完整工作流的代码实现
✅ 掌握 LCEL 链式调用语法
````
````
应用价值
🎯 企业级应用原型：可直接用于内部知识库、FAQ 机器人
🧩 模块化设计：可扩展多知识库、联网搜索、记忆功能
📈 代码可控：相比 Dify 可视化，代码实现更灵活、可定制
````
````
扩展方向
添加多轮对话记忆
支持多文档批量加载
接入重排序模型（Rerank）
尝试 Agent 和工具调用
````
