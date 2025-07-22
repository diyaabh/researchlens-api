from transformers import pipeline
from typing import Optional, List

# Load model once
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split the text into chunks of `chunk_size` characters.
    `overlap` helps preserve sentence continuity.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap  # slide with some overlap
    return chunks

def generate_summary(text: str, max_words: int = 130) -> Optional[str]:
    if not text or len(text) < 100:
        return None

    chunks = chunk_text(text, chunk_size=1000, overlap=100)
    summaries = []

    for chunk in chunks:
        try:
            result = summarizer(
                chunk,
                max_length=max_words,
                min_length=30,
                do_sample=False
            )
            summaries.append(result[0]["summary_text"])
        except Exception as e:
            print(f"Chunk summarization failed: {e}")
            continue

    final_summary = " ".join(summaries)
    return final_summary if final_summary else None
