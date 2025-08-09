# app/routers/qna.py

from fastapi import APIRouter, HTTPException, Path, Body
from pydantic import BaseModel, Field
from bson import ObjectId
from ..db import db
from ..services.qna_service import (
    chunk_text_by_words,
    build_faiss_index,
    top_k_chunks,
    answer_from_chunks,
)

router = APIRouter(prefix="/api", tags=["Q&A"])

class AskBody(BaseModel):
    question: str = Field(..., min_length=3, description="Your question about the document")
    k: int = Field(5, ge=1, le=15, description="Number of context chunks to retrieve")


@router.post("/ask-question/{doc_id}")
async def ask_question(
    doc_id: str = Path(..., description="MongoDB document ID"),
    body: AskBody = Body(...)
):
    # 1) Validate ID and fetch paper
    try:
        obj_id = ObjectId(doc_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid document ID")

    paper = await db.papers.find_one({"_id": obj_id})
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    raw_text = paper.get("raw_text", "") or ""
    if len(raw_text) < 100:
        raise HTTPException(status_code=422, detail="Document has too little text for Q&A")

    # 2) Chunk + index
    chunks = chunk_text_by_words(raw_text, chunk_words=180, overlap_words=30)
    if not chunks:
        raise HTTPException(status_code=422, detail="Failed to chunk document")

    index, chunks_ref = build_faiss_index(chunks)

    # 3) Retrieve top-k relevant chunks
    retrieved = top_k_chunks(body.question, index, chunks_ref, k=body.k)
    if not retrieved:
        raise HTTPException(status_code=422, detail="No relevant chunks found")

    # 4) Generate answer from top chunks
    answer = answer_from_chunks(body.question, retrieved)

    return {
        "doc_id": doc_id,
        "question": body.question,
        "answer": answer,
        "used_chunks": retrieved,   # helpful for debugging; remove later if noisy
    }
