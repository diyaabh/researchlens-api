# test_qna.py (in root folder for quick testing)

from app.services.qna_service import create_embeddings, find_top_k_chunks

text_chunks = [
    "The Transformer model uses self-attention for sequence modeling.",
    "It replaces recurrence with multi-head attention layers.",
    "The architecture is highly parallelizable.",
    "Attention mechanisms compute relevance between tokens.",
    "Sequence transduction has many applications like translation."
]

create_embeddings(text_chunks)

question = "What is self-attention used for?"
top_chunks = find_top_k_chunks(question, text_chunks)

print("Top relevant chunks:\n")
for chunk in top_chunks:
    print("-", chunk)
