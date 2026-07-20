# mcp_server/server.py
import os
from mcp.server.fastmcp import FastMCP
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


# 封装后的检索逻辑
class DocumentRetriever:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

    _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    _vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=_embeddings)

    @classmethod
    def get_relevant_context(cls, query: str):
        try:
            docs = cls._vectorstore.similarity_search(query, k=3)
            return "\n".join([doc.page_content for doc in docs])
        except Exception as e:
            return f"检索失败: {str(e)}"


# 初始化
mcp = FastMCP("Miemie-Knowledge-Server")


# 统一对外接口
@mcp.tool()
def retrieve_ai_papers(query: str) -> str:
    """设计 AI 架构时调用，返回本地向量库中的前沿技术事实。"""
    return DocumentRetriever.get_relevant_context(query)