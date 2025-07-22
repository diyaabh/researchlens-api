from fastapi import FastAPI
from .routers import upload

app = FastAPI(title="ResearchLens API", version="0.1.0")
app.include_router(upload.router)
