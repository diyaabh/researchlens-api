# ResearchLens API

ResearchLens is a multi-user, AI-powered API that allows users to upload academic papers or documents (PDFs), extract structured content, and generate intelligent summaries using NLP models.

## Features

- Upload and parse PDF documents via API
- Extract raw text from the uploaded PDFs
- Generate summaries using HuggingFace Transformers (BART)
- Supports chunked summarization for long documents
- MongoDB backend for document storage
- Built with FastAPI for high performance

## Tech Stack

- Language: Python 3.10+
- API Framework: FastAPI
- PDF Parsing: PyMuPDF (fitz)
- NLP Models: HuggingFace Transformers (bart-large-cnn)
- Database: MongoDB (via Motor - async client)
- Development Server: Uvicorn

## Project Structure

app/
├── main.py             # FastAPI entrypoint
├── config.py           # Environment and DB setup
├── db.py               # MongoDB async connection
├── routers/
│   └── upload.py       # PDF upload and routing logic
├── services/
│   ├── pdf_service.py  # PDF text extraction logic
│   └── summarizer.py   # Summarization logic

## Setup Instructions

1. Clone this repository:

   git clone https://github.com/your-username/researchlens-api.git
   cd researchlens-api

2. Create a virtual environment and activate it:

   python -m venv venv
   venv\Scripts\activate   # for Windows

3. Install dependencies:

   pip install -r requirements.txt

4. Create a `.env` file and add your MongoDB URI:

   MONGO_URI=mongodb://localhost:27017

5. Run the development server:

   uvicorn app.main:app --reload

6. Open your browser and test the API at:

   http://127.0.0.1:8000/docs

## API Endpoints

- POST /api/upload-paper  
  Upload a PDF and extract its content. Returns the document ID and page count.

- GET /api/summary/{doc_id}  
  Generate a summary from the parsed document content.

## What's Next

- Citation extraction from research papers
- Q&A over documents using transformer models
- JWT-based user authentication and session management
- Frontend UI with Streamlit or React
- Deployment to Railway, Render, or EC2

## Author

Diya Bhardwaj  
ResearchLens API — Built for intelligent document understanding

## License

MIT License
