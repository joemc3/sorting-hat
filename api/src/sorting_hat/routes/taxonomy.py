from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from sorting_hat.db import get_session
from sorting_hat.schemas.taxonomy import (
    GovernanceGroupCreate,
    GovernanceGroupResponse,
    GovernanceGroupUpdate,
    TaxonomyNodeCreate,
    TaxonomyNodeDetail,
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
    """List all governance groups, ordered by sort_order."""
    return await service.list_governance_groups()


@router.get("/governance-groups/{slug}", response_model=GovernanceGroupResponse)
async def get_governance_group(slug: str, service: TaxonomyService = Depends(get_service)):
    """Get a single governance group by its URL slug."""
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
    """Create a new governance group. The slug must be unique."""
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
    """Update a governance group. Only provided fields are changed."""
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
    """Delete a governance group. Fails if the group still has taxonomy nodes."""
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
    branch: str | None = Query(None, description="Filter by top-level branch: 'software' or 'computing-hardware'"),
    governance_group: str | None = Query(None, description="Filter by governance group slug"),
    max_depth: int | None = Query(None, description="Limit results to nodes at or above this tree depth"),
    service: TaxonomyService = Depends(get_service),
):
    """List taxonomy nodes with optional filters for branch, governance group, and depth."""
    return await service.list_nodes(branch, governance_group, max_depth)


@router.get("/nodes/search", response_model=list[TaxonomyNodeResponse])
async def search_nodes(
    q: str = Query(..., min_length=2, description="Text to search for in node names and definitions"),
    service: TaxonomyService = Depends(get_service),
):
    """Search taxonomy nodes by name or definition text."""
    return await service.search_nodes(q)


@router.get("/nodes/{node_id}", response_model=TaxonomyNodeDetail)
async def get_node(node_id: str, service: TaxonomyService = Depends(get_service)):
    """Get a taxonomy node with its children and full parent chain."""
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
    """Get all descendants of a taxonomy node as a flat list."""
    return await service.get_subtree(node_id)


@router.post("/nodes", response_model=TaxonomyNodeResponse, status_code=201)
async def create_node(
    data: TaxonomyNodeCreate,
    service: TaxonomyService = Depends(get_service),
    session: AsyncSession = Depends(get_session),
):
    """Create a new taxonomy node. Provide a parent_id to place it in the tree."""
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
    """Update a taxonomy node. Only provided fields are changed."""
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
    """Delete a taxonomy node. Fails if the node has children."""
    try:
        deleted = await service.delete_node(node_id)
    except TaxonomyServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not deleted:
        raise HTTPException(status_code=404, detail="Node not found")
    await session.commit()
