from datetime import datetime

from pydantic import BaseModel, Field


class GovernanceGroupBase(BaseModel):
    name: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=200)
    description: str = ""
    covers_software: bool = True
    covers_hardware: bool = False
    sort_order: int = 0


class GovernanceGroupCreate(GovernanceGroupBase):
    pass


class GovernanceGroupUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    description: str | None = None
    covers_software: bool | None = None
    covers_hardware: bool | None = None
    sort_order: int | None = None


class GovernanceGroupResponse(GovernanceGroupBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaxonomyNodeBase(BaseModel):
    name: str = Field(..., max_length=300)
    slug: str = Field(..., max_length=300)
    branch: str
    definition: str = ""
    distinguishing_characteristics: str = ""
    inclusions: str = ""
    exclusions: str = ""
    sort_order: int = 0


class TaxonomyNodeCreate(TaxonomyNodeBase):
    parent_id: str | None = None


class TaxonomyNodeUpdate(BaseModel):
    name: str | None = Field(None, max_length=300)
    definition: str | None = None
    distinguishing_characteristics: str | None = None
    inclusions: str | None = None
    exclusions: str | None = None
    sort_order: int | None = None


class TaxonomyNodeResponse(TaxonomyNodeBase):
    id: str
    governance_group_id: str
    parent_id: str | None
    path: str
    level: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaxonomyNodeDetail(TaxonomyNodeResponse):
    children: list[TaxonomyNodeResponse] = []
    parent_chain: list[TaxonomyNodeResponse] = []


class TaxonomyNodeMove(BaseModel):
    new_parent_id: str
