# app/services/qna_service.py

from typing import List, Tuple
import faiss
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# --- Load models once (fast after first run) ---
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # 384-dim vectors
EMBED_DIM = 384

# Extractive QA (answers from provided context)
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")


# ---------- Text utils ----------

def chunk_text_by_words(text: str, chunk_words: int = 180, overlap_words: int = 30) -> List[str]:
    """
    Split text into word-based chunks (better than raw char slicing).
    Keeps some overlap so we don't cut important sentences.
    """
    words = text.split()
    chunks = []
    start = 0
    n = len(words)

    while start < n:
        end = min(start + chunk_words, n)
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == n:
            break
        # slide with overlap
        start = max(0, end - overlap_words)

    return chunks


# ---------- Embeddings + Index ----------

def build_faiss_index(chunks: List[str]) -> Tuple[faiss.IndexFlatL2, List[str]]:
    """
    Embed chunks and build an in-memory FAISS index.
    Returns (index, chunks) for searching.
    """
    vectors = embedding_model.encode(chunks)  # shape: (N, 384)
    index = faiss.IndexFlatL2(EMBED_DIM)
    index.add(vectors)
    return index, chunks


def top_k_chunks(question: str, index: faiss.IndexFlatL2, chunks: List[str], k: int = 5) -> List[str]:
    """
    Search the FAISS index for k most similar chunks to the question.
    """
    q_vec = embedding_model.encode([question])  # shape: (1, 384)
    distances, indices = index.search(q_vec, k)
    return [chunks[i] for i in indices[0] if 0 <= i < len(chunks)]


# ---------- Answering ----------

def answer_from_chunks(question: str, chunks: List[str], max_context_chars: int = 3000) -> str:
    """
    Concatenate top chunks (bounded by max_context_chars) and run extractive QA.
    """
    # Keep concatenating chunks until we hit limit (to avoid model overflow)
    context_parts = []
    total = 0
    for c in chunks:
        if total + len(c) + 1 > max_context_chars:
            break
        context_parts.append(c)
        total += len(c) + 1

    context = "\n".join(context_parts).strip()

    if not context:
        return "Not enough relevant context found to answer the question."

    try:
        result = qa_pipeline(question=question, context=context)
        # result has keys: 'score', 'start', 'end', 'answer'
        answer = result.get("answer", "").strip()
        if not answer:
            return "I couldn't extract a confident answer from the document."
        return answer
    except Exception as e:
        return f"QA model error: {e}"
