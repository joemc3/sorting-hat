from datetime import datetime

from pydantic import BaseModel, Field


class GovernanceGroupBase(BaseModel):
    name: str = Field(..., max_length=200, description="Display name of the governance group")
    slug: str = Field(..., max_length=200, description="URL-friendly identifier (unique)")
    description: str = Field("", description="What this governance group covers")
    covers_software: bool = Field(True, description="Whether this group governs software categories")
    covers_hardware: bool = Field(False, description="Whether this group governs computing hardware categories")
    sort_order: int = Field(0, description="Display ordering (lower numbers appear first)")


class GovernanceGroupCreate(GovernanceGroupBase):
    """Create a new governance group."""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Infrastructure & Operations",
                    "slug": "infrastructure-operations",
                    "description": "Standards for infrastructure platforms, monitoring, and IT operations tooling",
                    "covers_software": True,
                    "covers_hardware": True,
                    "sort_order": 1,
                }
            ]
        }
    }


class GovernanceGroupUpdate(BaseModel):
    """Update fields on a governance group. Only include fields you want to change."""

    name: str | None = Field(None, max_length=200, description="New display name")
    description: str | None = Field(None, description="New description")
    covers_software: bool | None = Field(None, description="Whether this group governs software categories")
    covers_hardware: bool | None = Field(None, description="Whether this group governs computing hardware categories")
    sort_order: int | None = Field(None, description="New display ordering")


class GovernanceGroupResponse(GovernanceGroupBase):
    id: str = Field(..., description="Unique identifier (UUID)")
    created_at: datetime = Field(..., description="When the group was created")
    updated_at: datetime = Field(..., description="When the group was last modified")

    model_config = {"from_attributes": True}


class TaxonomyNodeBase(BaseModel):
    name: str = Field(..., max_length=300, description="Display name of the taxonomy node")
    slug: str = Field(..., max_length=300, description="URL-friendly identifier")
    branch: str = Field(..., description="Top-level branch: 'software' or 'computing-hardware'")
    definition: str = Field("", description="What products in this category do")
    distinguishing_characteristics: str = Field("", description="How to differentiate this category from similar ones")
    inclusions: str = Field("", description="Types of products that belong in this category")
    exclusions: str = Field("", description="Types of products that do NOT belong in this category")
    sort_order: int = Field(0, description="Display ordering within siblings (lower numbers first)")


class TaxonomyNodeCreate(TaxonomyNodeBase):
    """Create a new taxonomy node. Set parent_id to place it under an existing node."""

    parent_id: str | None = Field(None, description="UUID of the parent node (null for root-level nodes)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Container Orchestration",
                    "slug": "container-orchestration",
                    "branch": "software",
                    "definition": "Platforms that automate deployment, scaling, and management of containerized applications",
                    "distinguishing_characteristics": "Manages container lifecycle across clusters, not individual container runtimes",
                    "inclusions": "Kubernetes distributions, container scheduling platforms",
                    "exclusions": "Container runtimes (Docker Engine), CI/CD pipelines, serverless platforms",
                    "parent_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    "sort_order": 0,
                }
            ]
        }
    }


class TaxonomyNodeUpdate(BaseModel):
    """Update fields on a taxonomy node. Only include fields you want to change."""

    name: str | None = Field(None, max_length=300, description="New display name")
    definition: str | None = Field(None, description="New definition")
    distinguishing_characteristics: str | None = Field(None, description="New distinguishing characteristics")
    inclusions: str | None = Field(None, description="New inclusions text")
    exclusions: str | None = Field(None, description="New exclusions text")
    sort_order: int | None = Field(None, description="New display ordering")


class TaxonomyNodeResponse(TaxonomyNodeBase):
    id: str = Field(..., description="Unique identifier (UUID)")
    governance_group_id: str = Field(..., description="UUID of the governance group that owns this node")
    parent_id: str | None = Field(..., description="UUID of the parent node (null for root-level nodes)")
    path: str = Field(..., description="Materialized path in the tree (e.g. 'root.child.grandchild')")
    level: int = Field(..., description="Depth in the tree (0 = root)")
    created_at: datetime = Field(..., description="When the node was created")
    updated_at: datetime = Field(..., description="When the node was last modified")

    model_config = {"from_attributes": True}


class TaxonomyNodeDetail(TaxonomyNodeResponse):
    """A taxonomy node with its direct children and full ancestry chain."""

    children: list[TaxonomyNodeResponse] = Field([], description="Direct child nodes")
    parent_chain: list[TaxonomyNodeResponse] = Field([], description="Ancestor nodes from root to parent")


class TaxonomyNodeMove(BaseModel):
    new_parent_id: str = Field(..., description="UUID of the new parent node")
