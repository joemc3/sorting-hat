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
    ClassificationStepResponse,
    ClassifyRequest,
)
from sorting_hat.services.classifier import ClassifierService, ClassificationError

router = APIRouter(prefix="/classify", tags=["classification"])


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
    return result.classification


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
    return classification


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
    return list(result.scalars().all())
