from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sorting_hat.config import settings
from sorting_hat.routes import taxonomy_router, classification_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


tags_metadata = [
    {
        "name": "taxonomy",
        "description": "Manage the classification taxonomy: governance groups and taxonomy nodes. "
        "Governance groups represent organizational standards teams. "
        "Taxonomy nodes form the hierarchical tree used to classify products by capability.",
    },
    {
        "name": "classification",
        "description": "Classify products by URL. Submit a product webpage and the API uses AI "
        "to read the page, summarize the product, and classify it into the taxonomy. "
        "Supports retrieving past classifications with full audit trails.",
    },
]

app = FastAPI(
    title="The Sorting Hat",
    version="0.1.0",
    description=(
        "An API for classifying enterprise software and computing hardware by product capability. "
        "The Sorting Hat maintains a hierarchical taxonomy of ~220+ nodes across 10 governance groups, "
        "and uses AI to classify products into the correct taxonomy node(s) based on their public webpage.\n\n"
        "**Key concepts:**\n"
        "- **Governance Groups** — organizational teams that own sections of the taxonomy\n"
        "- **Taxonomy Nodes** — the hierarchical categories products are classified into\n"
        "- **Classification** — AI-driven analysis that assigns a primary node and up to two secondary nodes to a product"
    ),
    lifespan=lifespan,
    openapi_tags=tags_metadata,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(taxonomy_router, prefix=settings.api_prefix)
app.include_router(classification_router, prefix=settings.api_prefix)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
