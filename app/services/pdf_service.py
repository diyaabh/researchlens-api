import fitz  # PyMuPDF
from typing import Tuple, Dict

SECTION_HEADINGS = ["abstract", "introduction", "methods", "results", "discussion", "conclusion", "references"]

def extract_text_sections(file_bytes: bytes) -> Tuple[str, Dict[str, str], int]:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = "\n".join([page.get_text() for page in doc])
    num_pages = doc.page_count

    lower_text = full_text.lower()
    sections = {}
    for i, heading in enumerate(SECTION_HEADINGS):
        start = lower_text.find(heading)
        if start == -1:
            continue
        end = lower_text.find(SECTION_HEADINGS[i + 1]) if i + 1 < len(SECTION_HEADINGS) else len(full_text)
        sections[heading] = full_text[start:end].strip()

    return full_text, sections, num_pages
