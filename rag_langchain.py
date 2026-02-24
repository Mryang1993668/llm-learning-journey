"""
RAG 实战：基于 LangChain 官方阿里云组件的公司知识助手
完全使用 LangChain 官方提供的 DashScope 集成
"""

import os
from dotenv import load_dotenv

# LangChain 官方阿里云组件
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings

# LangChain 核心组件
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 加载环境变量
load_dotenv()

print("="*60)
print("🚀 RAG 实战：公司知识助手（LangChain 官方阿里云版）")
print("="*60)

# ============ 1. 初始化组件（对应 Dify 的模型供应商）============

# 1.1 初始化 LLM - 使用官方 ChatTongyi
# 注意：这里改用阿里云的 qwen-plus，因为 deepseek 可能不支持流式
llm = ChatTongyi(
    model="qwen-plus",  # 阿里云百炼的模型
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
    streaming=False,  # 先关掉流式，避免问题
    temperature=0.1,
)

# 1.2 初始化 Embedding 模型 - 使用官方 DashScopeEmbeddings
embeddings = DashScopeEmbeddings(
    model="text-embedding-v3",  # 使用 v3 版本
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
)

print(f"\n📊 配置信息：")
print(f"   LLM 模型：qwen-plus")
print(f"   Embedding 模型：text-embedding-v3")

# ============ 2. 知识库构建 =============

def create_vector_store(file_path="公司员工手册.txt", force_recreate=False):
    """创建向量知识库"""

    index_path = "faiss_index"

    # 如果已存在且不强制重建，直接加载
    if os.path.exists(index_path) and not force_recreate:
        print("\n📚 发现已有向量库，直接加载...")
        vectorstore = FAISS.load_local(
            index_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        print("✅ 向量库加载完成")
        return vectorstore

    print(f"\n📄 正在加载文档：{file_path}")

    # 加载文档
    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()
    print(f"   文档加载成功，共 {len(documents)} 篇")

    # 文本分块
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", " ", ""],
    )
    docs = text_splitter.split_documents(documents)
    print(f"   文档切分为 {len(docs)} 个片段")

    # 创建向量库
    print("   正在生成向量索引（调用阿里云 Embedding）...")
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(index_path)
    print(f"✅ 向量库创建完成，已保存到 {index_path} 文件夹")

    return vectorstore

# ============ 3. 创建检索器 =============

def create_retriever(vectorstore, k=3):
    """创建检索器"""
    return vectorstore.as_retriever(
        search_kwargs={"k": k}
    )

# ============ 4. 提示词模板 =============

prompt_template = """你是一个专业的公司内部知识助手。

【知识库内容】
{context}

【回答要求】
1. 严格基于上述知识库内容回答问题
2. 如果知识库中没有相关信息，请说："抱歉，我的知识库中没有找到相关信息，请联系HR部门咨询"
3. 如果用户问的不是公司相关问题，请说："我是公司内部知识助手，只能回答公司相关的问题哦"
4. 回答要简洁明了，用列表形式呈现

【用户问题】
{question}

【回答】："""

prompt = ChatPromptTemplate.from_template(prompt_template)

# ============ 5. 构建 RAG 链 =============

def format_docs(docs):
    """格式化检索到的文档"""
    return "\n\n".join([doc.page_content for doc in docs])

def build_rag_chain(vectorstore):
    """构建 RAG 链"""

    retriever = create_retriever(vectorstore, k=3)

    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain

# ============ 6. 调试模式（显示检索结果）============

def build_debug_chain(vectorstore):
    """带调试信息的 RAG 链"""

    retriever = create_retriever(vectorstore, k=3)

    def debug_retrieve(question):
        print(f"\n🔍 [知识检索节点] 正在检索：{question}")
        docs = retriever.invoke(question)
        print(f"   召回 {len(docs)} 个相关片段：")
        for i, doc in enumerate(docs):
            print(f"   片段 {i+1}: {doc.page_content[:50]}...")
        return docs

    def debug_format(docs):
        print("📦 [上下文组装] 将检索结果拼接到提示词中")
        return format_docs(docs)

    debug_chain = (
        {
            "context": lambda x: debug_format(debug_retrieve(x)),
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return debug_chain

# ============ 7. 交互式问答 =============

def run_interactive():
    """交互式问答"""

    # 初始化向量库
    print("\n📚 第一步：初始化知识库")
    vectorstore = create_vector_store("公司员工手册.txt")

    # 选择模式
    print("\n⚙️ 第二步：选择运行模式")
    mode = input("请选择模式 [1=普通模式, 2=调试模式, 3=测试用例, 默认=1]: ").strip()

    if mode == "2":
        rag_chain = build_debug_chain(vectorstore)
        print("✅ 调试模式已开启")
    else:
        rag_chain = build_rag_chain(vectorstore)
        print("✅ 普通模式已开启")

    # 测试用例
    if mode == "3":
        print("\n🧪 运行预设测试用例：")
        test_cases = [
            "公司有什么福利？",
            "请假怎么请？",
            "你们公司卖什么产品？",
            "今天天气怎么样？"
        ]
        for q in test_cases:
            print(f"\n{'='*60}")
            print(f"问题：{q}")
            print('='*60)
            answer = rag_chain.invoke(q)
            print(f"答案：{answer}")
        return

    # 交互模式
    print("\n💬 第三步：开始问答（输入 'exit' 退出）")
    while True:
        question = input("\n❓ 请输入问题：")
        if question.lower() in ['exit', 'quit', 'q']:
            break

        print("\n⏳ 正在思考...")
        answer = rag_chain.invoke(question)
        print(f"\n💡 答案：{answer}")

# ============ 8. 主程序 =============

if __name__ == "__main__":
    # 检查环境变量
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("❌ 错误：未找到 DASHSCOPE_API_KEY 环境变量")
        print("请在 .env 文件中设置：DASHSCOPE_API_KEY=sk-xxx")
        exit(1)

    run_interactive()