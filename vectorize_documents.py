# vectorize_documents.py
"""
Reads PDF files from ./data, splits them into chunks, and stores embeddings in
./vector_db_dir using ChromaDB.

Chunks are tagged with the same topic names used by the UI buttons.
"""

import os
import platform
import sys
from collections import Counter

import pytesseract
from PyPDF2 import PdfReader
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


BUTTON_TOPIC_KEYWORDS = {
    "Study Stress": [
        "study", "student", "exam", "assignment", "academic", "school",
        "college", "deadline", "procrastination", "focus", "burnout",
    ],
    "Sleep Issues": [
        "sleep", "insomnia", "rest", "bedtime", "fatigue", "tired",
        "night", "wake", "routine", "circadian",
    ],
    "Relationships": [
        "relationship", "friend", "family", "partner", "conflict",
        "boundary", "communication", "lonely", "support", "trust",
    ],
    "Anxiety": [
        "anxiety", "anxious", "panic", "worry", "fear", "stress",
        "overthinking", "grounding", "breathing", "nervous",
    ],
}


def _configure_tesseract():
    if platform.system() == "Windows":
        default_win_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        env_path = os.environ.get("TESSERACT_PATH", default_win_path)
        if os.path.exists(env_path):
            pytesseract.pytesseract.tesseract_cmd = env_path
        else:
            print(
                f"[Warning] Tesseract not found at '{env_path}'. "
                "OCR will be unavailable. Set TESSERACT_PATH if needed."
            )


_configure_tesseract()


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
    pdf_files = [f for f in os.listdir(directory) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print(f"[Warning] No PDF files found in '{directory}'.")
        return []

    documents = []
    for pdf_file in pdf_files:
        file_path = os.path.join(directory, pdf_file)
        try:
            print(f"  Processing {pdf_file}...", end=" ", flush=True)
            reader = PdfReader(file_path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            documents.append(Document(page_content=text, metadata={"source": pdf_file}))
            print("OK")
        except Exception as exc:
            print(f"Failed ({exc})")

    return documents


def main():
    project_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(project_dir, "data")
    db_dir = os.path.join(project_dir, "vector_db_dir")

    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(db_dir, exist_ok=True)

    print("\n[1/4] Loading PDF documents...")
    documents = load_pdf_documents(data_dir)

    if not documents:
        print("No documents were loaded. Add PDF files to the 'data' folder and re-run.")
        sys.exit(1)

    print(f"      Loaded {len(documents)} document(s).")

    print("\n[2/4] Splitting documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=500,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    chunks = enrich_chunk_metadata(chunks)
    print(f"      Created {len(chunks)} tagged chunk(s).")

    print("\n[3/4] Loading HuggingFace embedding model...")
    embeddings = HuggingFaceEmbeddings()
    print("      Model ready.")

    print("\n[4/4] Building ChromaDB vector store...")
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=db_dir,
    )

    print(f"      Vector store saved to '{db_dir}'.")
    print("\nDone! Start the app with: streamlit run streamlit_app.py\n")


if __name__ == "__main__":
    main()