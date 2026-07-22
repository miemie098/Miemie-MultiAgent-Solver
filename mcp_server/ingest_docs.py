"""
Document ingestion pipeline: PDF + Markdown → text chunks → Milvus vector store.

Replaces the previous ChromaDB pipeline with Milvus (embedded mode) for
production-grade vector storage, matching the Miemie-Agent-RAG tech stack.
"""
import os
import sys

# Ensure the project root is on sys.path for imports
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from langchain_community.document_loaders import PyPDFDirectoryLoader, DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.services.retriever import get_retriever

# ── Paths ──────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(_PROJECT_ROOT, "data")
PDF_DIR = os.path.join(DATA_DIR, "pdfs")
MD_DIR = os.path.join(DATA_DIR, "markdowns")


def ingest_docs() -> int:
    """Load PDFs and Markdown docs, chunk them, and insert into Milvus.

    Returns the total number of chunks ingested.
    """
    docs = []

    # 1. Load PDFs
    if os.path.isdir(PDF_DIR) and os.listdir(PDF_DIR):
        print(f"⏳ Parsing PDFs from {PDF_DIR} ...")
        pdf_loader = PyPDFDirectoryLoader(PDF_DIR)
        loaded = pdf_loader.load()
        print(f"   Loaded {len(loaded)} PDF pages")
        docs.extend(loaded)
    else:
        print(f"⚠️  PDF directory empty or missing: {PDF_DIR}")

    # 2. Load Markdown / plain-text docs
    if os.path.isdir(MD_DIR) and os.listdir(MD_DIR):
        print(f"⏳ Parsing Markdown/text from {MD_DIR} ...")
        md_loader = DirectoryLoader(
            MD_DIR, glob="**/*.md", loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
        )
        txt_loader = DirectoryLoader(
            MD_DIR, glob="**/*.txt", loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
        )
        md_docs = md_loader.load()
        txt_docs = txt_loader.load()
        print(f"   Loaded {len(md_docs)} markdown + {len(txt_docs)} text files")
        docs.extend(md_docs)
        docs.extend(txt_docs)
    else:
        print(f"⚠️  Markdown directory empty or missing: {MD_DIR}")

    if not docs:
        print("❌ No documents found. Place PDFs in data/pdfs/ and markdown in data/markdowns/.")
        return 0

    # 3. Semantic chunking
    print(f"✂️  Chunking {len(docs)} document sources ...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)
    print(f"   Produced {len(splits)} text chunks")

    # 4. Insert into Milvus (which also builds BM25 index automatically)
    print("🧠 Embedding chunks and inserting into Milvus (first run downloads model) ...")
    retriever = get_retriever()
    count = retriever.insert([doc.page_content for doc in splits])
    print(f"🎉 Ingestion complete! {count} chunks stored in Milvus.")
    return count


if __name__ == "__main__":
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(MD_DIR, exist_ok=True)
    ingest_docs()
