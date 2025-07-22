from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from bson import ObjectId
from datetime import datetime
from ..db import db
from ..services.pdf_service import extract_text_sections
from fastapi import Path
from ..services.summarizer import generate_summary

router = APIRouter(prefix="/api")

# TEMP: Fake user auth stub (replace later with real auth)
async def get_current_user_id():
    return ObjectId("64b0e7b21faedba8fe000001")

@router.post("/upload-paper", status_code=status.HTTP_201_CREATED)
async def upload_paper(file: UploadFile = File(...),
                       user_id: ObjectId = Depends(get_current_user_id)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_bytes = await file.read()
    try:
        raw_text, sections, num_pages = extract_text_sections(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"PDF parsing error: {e}")

    paper_doc = {
        "user_id": user_id,
        "filename": file.filename,
        "upload_date": datetime.utcnow(),
        "num_pages": num_pages,
        "raw_text": raw_text,
        "sections": sections
    }

    result = await db.papers.insert_one(paper_doc)
    return {"doc_id": str(result.inserted_id), "num_pages": num_pages}


@router.get("/summary/{doc_id}")
async def summarize_paper(doc_id: str = Path(..., description="MongoDB document ID")):
    from bson import ObjectId
    from ..db import db

    try:
        obj_id = ObjectId(doc_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid document ID format")

    paper = await db.papers.find_one({"_id": obj_id})
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    raw_text = paper.get("raw_text", "")
    summary = generate_summary(raw_text)

    if not summary:
        raise HTTPException(status_code=422, detail="Could not generate summary (too short?)")

    return {"doc_id": doc_id, "summary": summary}
