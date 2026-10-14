import os
import pickle
import numpy as np
import faiss
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from groq import Groq

# Base project directory for reliable paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "processed_data")

# .env se API key load karna
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Global cache for data & models so they don't reload on every query
_CACHED_DATA = None

# Default Groq model (fallback to llama-3.3-70b-versatile)
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


def get_groq_client(api_key=None):
    """Groq client initialization with validation"""
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key or not key.strip() or key.strip() == "your_groq_api_key_here":
        raise ValueError(
            "GROQ_API_KEY is missing or invalid. Please add your Groq API key to the .env file."
        )
    return Groq(api_key=key.strip())


def load_all_data():
    """Saved chunks, embeddings aur FAISS index load karta hai (cached)"""
    global _CACHED_DATA
    if _CACHED_DATA is not None:
        return _CACHED_DATA

    embeddings_path = os.path.join(PROCESSED_DATA_DIR, "embeddings.npy")
    chunks_path = os.path.join(PROCESSED_DATA_DIR, "chunks.pkl")
    index_path = os.path.join(PROCESSED_DATA_DIR, "faiss_index.index")

    if not os.path.exists(chunks_path) or not os.path.exists(index_path):
        raise FileNotFoundError(
            f"Processed data files not found in '{PROCESSED_DATA_DIR}'. "
            "Please ensure chunks.pkl and faiss_index.index exist."
        )

    with open(chunks_path, "rb") as f:
        chunks = pickle.load(f)

    index = faiss.read_index(index_path)
    model = SentenceTransformer("all-MiniLM-L6-v2")

    _CACHED_DATA = (chunks, index, model)
    return _CACHED_DATA


def retrieve_chunks(query, model, index, chunks, top_k=4):
    """Sawal se relevant chunks nikaalta hai"""
    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding.astype("float32"), top_k)

    results = []
    for idx in indices[0]:
        if 0 <= idx < len(chunks):
            results.append(chunks[idx])

    return results


def generate_answer_from_notes(query, retrieved_chunks, api_key=None):
    """Notes (context) se answer"""
    client = get_groq_client(api_key=api_key)

    context = ""
    for i, chunk in enumerate(retrieved_chunks):
        context += f"\n--- Source {i+1} ({chunk['subject']} | {chunk['filename']}) ---\n"
        context += chunk["text"] + "\n"

    prompt = f"""You are a study assistant. Answer ONLY using the context below.
If the answer is not in the context, reply exactly with: I don't know based on the available notes.

Context:
{context}

Question: {query}

Answer:"""

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()


def generate_general_answer(query, api_key=None):
    """General knowledge se answer (notes ke bina)"""
    client = get_groq_client(api_key=api_key)

    prompt = f"""You are a helpful tutor for AI & Data Science / Computer Science students.
Answer clearly and concisely.

Question: {query}

Answer:"""

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()


def rag_query(query, api_key=None):
    """Returns: answer, sources, source_type ('notes' | 'general')"""
    chunks, index, model = load_all_data()
    retrieved = retrieve_chunks(query, model, index, chunks, top_k=4)
    answer = generate_answer_from_notes(query, retrieved, api_key=api_key)

    dont_know_phrases = [
        "i don't know based on the available notes",
        "i don't know",
        "not in the context",
        "not available in the notes",
        "no information",
    ]
    is_dont_know = any(p in answer.lower() for p in dont_know_phrases)

    if is_dont_know:
        return generate_general_answer(query, api_key=api_key), [], "general"

    return answer, retrieved, "notes"


