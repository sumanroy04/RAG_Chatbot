import os
import sys
import platform
from collections import Counter
import pytesseract
from PyPDF2 import PdfReader
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.app.config import DATA_DIR, VECTOR_DB_DIR
from backend.app.constants import BUTTON_TOPIC_KEYWORDS

def configure_tesseract():
    if platform.system() == "Windows":
        default_win_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        env_path = os.environ.get("TESSERACT_PATH", default_win_path)
        if os.path.exists(env_path):
            pytesseract.pytesseract.tesseract_cmd = env_path

configure_tesseract()

def detect_button_topics(text: str) -> list[str]:
    lowered = (text or "").lower()
    matched = []
    for topic, keywords in BUTTON_TOPIC_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            matched.append(topic)
    return matched

def primary_button_topic(text: str) -> str:
    lowered = (text or "").lower()
    scores = Counter()
    for topic, keywords in BUTTON_TOPIC_KEYWORDS.items():
        scores[topic] = sum(lowered.count(keyword) for keyword in keywords)

    if not scores or scores.most_common(1)[0][1] == 0:
        return "General"

    return scores.most_common(1)[0][0]

def enrich_chunk_metadata(chunks: list[Document]) -> list[Document]:
    for index, chunk in enumerate(chunks):
        topics = detect_button_topics(chunk.page_content)
        chunk.metadata = {
            **chunk.metadata,
            "chunk_index": index,
            "button_topics": ", ".join(topics) if topics else "General",
            "primary_topic": primary_button_topic(chunk.page_content),
        }
    return chunks

def load_pdf_documents(directory: str) -> list[Document]:
    if not os.path.exists(directory):
        return []
    pdf_files = [f for f in os.listdir(directory) if f.lower().endswith(".pdf")]

    if not pdf_files:
        return []

    documents = []
    for pdf_file in pdf_files:
        file_path = os.path.join(directory, pdf_file)
        try:
            reader = PdfReader(file_path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            documents.append(Document(page_content=text, metadata={"source": pdf_file}))
        except Exception:
            pass

    return documents

def setup_vectorstore():
    persist_directory = str(VECTOR_DB_DIR)
    embeddings = HuggingFaceEmbeddings()
    # Ensure directory exists
    os.makedirs(persist_directory, exist_ok=True)
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings)

def rebuild_vectorstore():
    """Builds/Rebuilds ChromaDB from scratch using documents in the data folder."""
    data_path = str(DATA_DIR)
    db_path = str(VECTOR_DB_DIR)
    
    os.makedirs(data_path, exist_ok=True)
    os.makedirs(db_path, exist_ok=True)

    documents = load_pdf_documents(data_path)
    if not documents:
        raise ValueError(f"No PDF files found in {data_path}. Add files to build DB.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=500,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    chunks = enrich_chunk_metadata(chunks)

    embeddings = HuggingFaceEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=db_path,
    )
    return vectorstore
