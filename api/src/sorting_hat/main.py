from fastapi import FastAPI

from sorting_hat.config import settings
from sorting_hat.routes import taxonomy_router, classification_router

app = FastAPI(title="The Sorting Hat", version="0.1.0")

app.include_router(taxonomy_router, prefix=settings.api_prefix)
app.include_router(classification_router, prefix=settings.api_prefix)


@app.get("/health")
async def health():
    return {"status": "ok"}
