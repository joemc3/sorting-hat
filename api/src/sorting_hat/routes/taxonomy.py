from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from sorting_hat.db import get_session
from sorting_hat.schemas.taxonomy import (
    GovernanceGroupCreate,
    GovernanceGroupResponse,
    GovernanceGroupUpdate,
    TaxonomyNodeCreate,
    TaxonomyNodeDetail,
    TaxonomyNodeMove,
    TaxonomyNodeResponse,
    TaxonomyNodeUpdate,
)
from sorting_hat.services.taxonomy import TaxonomyService, TaxonomyServiceError

router = APIRouter(prefix="/taxonomy", tags=["taxonomy"])


def get_service(session: AsyncSession = Depends(get_session)) -> TaxonomyService:
    return TaxonomyService(session)


# --- Governance Groups ---


@router.get("/governance-groups", response_model=list[GovernanceGroupResponse])
async def list_governance_groups(service: TaxonomyService = Depends(get_service)):
    return await service.list_governance_groups()


@router.get("/governance-groups/{slug}", response_model=GovernanceGroupResponse)
async def get_governance_group(slug: str, service: TaxonomyService = Depends(get_service)):
    group = await service.get_governance_group(slug)
    if not group:
        raise HTTPException(status_code=404, detail="Governance group not found")
    return group


@router.post("/governance-groups", response_model=GovernanceGroupResponse, status_code=201)
async def create_governance_group(
    data: GovernanceGroupCreate,
    service: TaxonomyService = Depends(get_service),
    session: AsyncSession = Depends(get_session),
):
    group = await service.create_governance_group(data)
    await session.commit()
    return group


@router.put("/governance-groups/{slug}", response_model=GovernanceGroupResponse)
async def update_governance_group(
    slug: str,
    data: GovernanceGroupUpdate,
    service: TaxonomyService = Depends(get_service),
    session: AsyncSession = Depends(get_session),
):
    group = await service.update_governance_group(slug, data)
    if not group:
        raise HTTPException(status_code=404, detail="Governance group not found")
    await session.commit()
    return group


@router.delete("/governance-groups/{slug}", status_code=204)
async def delete_governance_group(
    slug: str,
    service: TaxonomyService = Depends(get_service),
    session: AsyncSession = Depends(get_session),
):
    try:
        deleted = await service.delete_governance_group(slug)
    except TaxonomyServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not deleted:
        raise HTTPException(status_code=404, detail="Governance group not found")
    await session.commit()


# --- Taxonomy Nodes ---


@router.get("/nodes", response_model=list[TaxonomyNodeResponse])
async def list_nodes(
    branch: str | None = None,
    governance_group: str | None = None,
    max_depth: int | None = None,
    service: TaxonomyService = Depends(get_service),
):
    return await service.list_nodes(branch, governance_group, max_depth)


@router.get("/nodes/search", response_model=list[TaxonomyNodeResponse])
async def search_nodes(
    q: str = Query(..., min_length=1), service: TaxonomyService = Depends(get_service)
):
    return await service.search_nodes(q)


@router.get("/nodes/{node_id}", response_model=TaxonomyNodeDetail)
async def get_node(node_id: str, service: TaxonomyService = Depends(get_service)):
    node = await service.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    parent_chain = await service.get_parent_chain(node_id)
    return TaxonomyNodeDetail(
        **TaxonomyNodeResponse.model_validate(node).model_dump(),
        children=[TaxonomyNodeResponse.model_validate(c) for c in node.children],
        parent_chain=[TaxonomyNodeResponse.model_validate(p) for p in parent_chain],
    )


@router.get("/nodes/{node_id}/subtree", response_model=list[TaxonomyNodeResponse])
async def get_subtree(node_id: str, service: TaxonomyService = Depends(get_service)):
    return await service.get_subtree(node_id)


@router.post("/nodes", response_model=TaxonomyNodeResponse, status_code=201)
async def create_node(
    data: TaxonomyNodeCreate,
    service: TaxonomyService = Depends(get_service),
    session: AsyncSession = Depends(get_session),
):
    try:
        node = await service.create_node(data)
    except TaxonomyServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    await session.commit()
    return node


@router.put("/nodes/{node_id}", response_model=TaxonomyNodeResponse)
async def update_node(
    node_id: str,
    data: TaxonomyNodeUpdate,
    service: TaxonomyService = Depends(get_service),
    session: AsyncSession = Depends(get_session),
):
    node = await service.update_node(node_id, data)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    await session.commit()
    return node


@router.delete("/nodes/{node_id}", status_code=204)
async def delete_node(
    node_id: str,
    service: TaxonomyService = Depends(get_service),
    session: AsyncSession = Depends(get_session),
):
    try:
        deleted = await service.delete_node(node_id)
    except TaxonomyServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not deleted:
        raise HTTPException(status_code=404, detail="Node not found")
    await session.commit()
