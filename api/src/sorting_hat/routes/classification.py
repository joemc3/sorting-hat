from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sorting_hat.config import settings
from sorting_hat.db import get_session
from sorting_hat.llm import OpenAICompatProvider
from sorting_hat.models.classification import Classification
from sorting_hat.schemas.classification import (
    ClassificationDetail,
    ClassificationResponse,
    ClassifyRequest,
)
from sorting_hat.services.classifier import ClassifierService, ClassificationError
from sorting_hat.services.taxonomy import TaxonomyService

router = APIRouter(prefix="/classify", tags=["classification"])


async def _resolve_node_paths(
    classification: Classification, session: AsyncSession
) -> ClassificationResponse:
    """Build a response dict with human-readable node paths resolved."""
    taxonomy = TaxonomyService(session)
    response = ClassificationResponse.model_validate(classification)

    if classification.primary_node_id:
        response.primary_node_path = await taxonomy.resolve_node_path(
            classification.primary_node_id
        )

    paths = []
    for node_id in classification.secondary_node_ids:
        path = await taxonomy.resolve_node_path(node_id)
        if path:
            paths.append(path)
    response.secondary_node_paths = paths

    return response


def get_llm_provider() -> OpenAICompatProvider:
    return OpenAICompatProvider(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url if settings.llm_base_url else None,
    )


@router.post("", response_model=ClassificationResponse, status_code=201)
async def classify_url(
    data: ClassifyRequest,
    session: AsyncSession = Depends(get_session),
    provider: OpenAICompatProvider = Depends(get_llm_provider),
):
    model = data.model or settings.llm_model
    service = ClassifierService(session=session, llm=provider, model=model)
    try:
        result = await service.classify_url(data.url)
    except ClassificationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {e}")
    await session.commit()
    return await _resolve_node_paths(result.classification, session)


@router.get("/{classification_id}", response_model=ClassificationDetail)
async def get_classification(
    classification_id: str, session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Classification)
        .where(Classification.id == classification_id)
        .options(selectinload(Classification.steps))
    )
    classification = result.scalar_one_or_none()
    if not classification:
        raise HTTPException(status_code=404, detail="Classification not found")

    taxonomy = TaxonomyService(session)
    response = ClassificationDetail.model_validate(classification)
    if classification.primary_node_id:
        response.primary_node_path = await taxonomy.resolve_node_path(
            classification.primary_node_id
        )
    paths = []
    for node_id in classification.secondary_node_ids:
        path = await taxonomy.resolve_node_path(node_id)
        if path:
            paths.append(path)
    response.secondary_node_paths = paths
    return response


@router.get("", response_model=list[ClassificationResponse])
async def list_classifications(
    url: str | None = None,
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    query = select(Classification).order_by(Classification.created_at.desc())
    if url:
        query = query.where(Classification.url.ilike(f"%{url}%"))
    query = query.limit(limit).offset(offset)
    result = await session.execute(query)
    classifications = list(result.scalars().all())
    return [await _resolve_node_paths(c, session) for c in classifications]
