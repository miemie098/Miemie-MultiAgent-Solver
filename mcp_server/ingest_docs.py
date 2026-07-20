# mcp_server/ingest_docs.py
import os
from langchain_community.document_loaders import PyPDFDirectoryLoader, DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# 定义路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PDF_DIR = os.path.join(DATA_DIR, "pdfs")
MD_DIR = os.path.join(DATA_DIR, "markdowns")  # 🌟 新增：专门存放 Markdown/TXT 格式技术文档的目录
DB_DIR = os.path.join(DATA_DIR, "chroma_db")


def ingest_docs_to_chroma():
    docs = []

    # 1. 扫描并加载 PDF 文件
    if os.path.exists(PDF_DIR) and os.listdir(PDF_DIR):
        print(f"⏳ 正在解析 PDF 内容 ({PDF_DIR})...")
        pdf_loader = PyPDFDirectoryLoader(PDF_DIR)
        docs.extend(pdf_loader.load())
    else:
        print(f"⚠️ 提示: {PDF_DIR} 为空或不存在。")

    # 2. 🌟 扫描并加载 Markdown / TXT 技术文档（面试加分项：多格式解析）
    if os.path.exists(MD_DIR) and os.listdir(MD_DIR):
        print(f"⏳ 正在解析 Markdown/纯文本 内容 ({MD_DIR})...")
        md_loader = DirectoryLoader(MD_DIR, glob="**/*.md", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'})
        txt_loader = DirectoryLoader(MD_DIR, glob="**/*.txt", loader_cls=TextLoader,loader_kwargs={'encoding': 'utf-8'})
        docs.extend(md_loader.load())
        docs.extend(txt_loader.load())
    else:
        print(f"⚠️ 提示: {MD_DIR} 为空或不存在。建议放入一些 .md 格式的官方文档以丰富知识库。")

    # 兜底防御
    if not docs:
        print("❌ 错误：没有找到任何文档！请先在 data/pdfs/ 或 data/markdowns/ 中放入技术资料。")
        return

    # 3. 文本切片 (Chunking) - 保证每块包含完整语义
    print(f"✂️ 正在进行语义切片 (共读取到 {len(docs)} 个文档源)...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    splits = text_splitter.split_documents(docs)
    print(f"✅ 共切分为 {len(splits)} 个文本块。")

    # 4. 向量化并灌入 ChromaDB
    print("🧠 正在进行向量化并存入本地数据库 (首次运行需下载模型)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 覆盖式写入新的向量库
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    print(f"🎉 知识库灌入完成！数据库已持久化至: {DB_DIR}")


if __name__ == "__main__":
    # 自动创建缺失的文件夹，提升开发者体验
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(MD_DIR, exist_ok=True)

    ingest_docs_to_chroma()