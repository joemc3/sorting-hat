from fastapi import FastAPI

from sorting_hat.config import settings

app = FastAPI(title="The Sorting Hat", version="0.1.0")


@app.get("/health")
async def health():
    return {"status": "ok"}
