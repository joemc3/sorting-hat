# The Sorting Hat — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the full Sorting Hat product: a FastAPI backend with taxonomy management + AI classification APIs, a Next.js front end, and a Supabase database — from an empty repo to working system.

**Architecture:** Monorepo with `api/` (Python FastAPI), `web/` (Next.js + shadcn/ui), and `supabase/` (migrations). FastAPI owns all business logic and is the only service that talks to Postgres. The classification pipeline is scrape → summarize → classify with provider-agnostic LLM support.

**Tech Stack:** Python 3.12+, FastAPI, SQLAlchemy 2.0, Alembic, httpx, trafilatura, pytest. Node 20+, Next.js 15 (App Router), Tailwind CSS, shadcn/ui. PostgreSQL via Supabase (ltree extension).

**Reference docs:**
- `docs/plans/2026-02-06-sorting-hat-design.md` — Validated system design
- `research/Draft v0.2 - Taxonomy Structure.md` — Full taxonomy tree
- `research/Taxonomy Definitions - Complete Reference.md` — Node definitions for seeding

---

## Task 1: Python API Project Scaffolding

**Files:**
- Create: `api/pyproject.toml`
- Create: `api/src/sorting_hat/__init__.py`
- Create: `api/src/sorting_hat/main.py`
- Create: `api/src/sorting_hat/config.py`
- Create: `api/tests/__init__.py`
- Create: `api/tests/conftest.py`
- Create: `api/tests/test_health.py`

**Step 1: Create `api/pyproject.toml`**

```toml
[project]
name = "sorting-hat-api"
version = "0.1.0"
description = "The Sorting Hat — taxonomy management and classification API"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "httpx>=0.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "httpx>=0.28.0",
    "ruff>=0.9.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
target-version = "py312"
line-length = 100
```

**Step 2: Create `api/src/sorting_hat/config.py`**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://localhost:5432/sorting_hat"
    api_prefix: str = "/api/v1"
    debug: bool = False

    model_config = {"env_prefix": "SORTING_HAT_", "env_file": ".env"}


settings = Settings()
```

**Step 3: Create `api/src/sorting_hat/main.py`**

```python
from fastapi import FastAPI

from sorting_hat.config import settings

app = FastAPI(title="The Sorting Hat", version="0.1.0")


@app.get("/health")
async def health():
    return {"status": "ok"}
```

**Step 4: Create `api/src/sorting_hat/__init__.py`**

```python
```

(Empty file.)

**Step 5: Write the failing test — `api/tests/test_health.py`**

```python
from fastapi.testclient import TestClient

from sorting_hat.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

**Step 6: Create `api/tests/__init__.py` and `api/tests/conftest.py`**

`api/tests/__init__.py` — empty file.

```python
# api/tests/conftest.py
```

(Empty for now. Will hold database fixtures later.)

**Step 7: Install dependencies and run test**

```bash
cd api && pip install -e ".[dev]" && pytest tests/test_health.py -v
```

Expected: PASS — `test_health_returns_ok` passes.

**Step 8: Verify the server starts**

```bash
cd api && uvicorn sorting_hat.main:app --port 8000 &
sleep 2 && curl http://localhost:8000/health && kill %1
```

Expected: `{"status":"ok"}`

**Step 9: Commit**

```bash
git add api/
git commit -m "feat: scaffold FastAPI project with health endpoint and tests"
```

---

## Task 2: Database Schema & Models

**Files:**
- Create: `api/src/sorting_hat/db.py`
- Create: `api/src/sorting_hat/models/__init__.py`
- Create: `api/src/sorting_hat/models/taxonomy.py`
- Create: `api/src/sorting_hat/models/classification.py`
- Create: `supabase/migrations/001_initial_schema.sql`
- Create: `api/alembic.ini`
- Create: `api/alembic/env.py`
- Create: `api/alembic/script.mako`
- Create: `api/alembic/versions/.gitkeep`
- Create: `api/tests/test_models.py`

**Step 1: Create `api/src/sorting_hat/db.py`**

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sorting_hat.config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
```

**Step 2: Create `api/src/sorting_hat/models/taxonomy.py`**

```python
import enum
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Branch(str, enum.Enum):
    software = "software"
    hardware = "hardware"


class GovernanceGroup(Base):
    __tablename__ = "governance_groups"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    covers_software: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    covers_hardware: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    nodes: Mapped[list["TaxonomyNode"]] = relationship(back_populates="governance_group")


class TaxonomyNode(Base):
    __tablename__ = "taxonomy_nodes"
    __table_args__ = (UniqueConstraint("parent_id", "slug", name="uq_node_parent_slug"),)

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    governance_group_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("governance_groups.id"), nullable=False
    )
    parent_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("taxonomy_nodes.id"), nullable=True
    )
    path: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    branch: Mapped[Branch] = mapped_column(Enum(Branch), nullable=False)
    definition: Mapped[str] = mapped_column(Text, nullable=False, default="")
    distinguishing_characteristics: Mapped[str] = mapped_column(
        Text, nullable=False, default=""
    )
    inclusions: Mapped[str] = mapped_column(Text, nullable=False, default="")
    exclusions: Mapped[str] = mapped_column(Text, nullable=False, default="")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    governance_group: Mapped[GovernanceGroup] = relationship(back_populates="nodes")
    parent: Mapped["TaxonomyNode | None"] = relationship(
        back_populates="children", remote_side=[id]
    )
    children: Mapped[list["TaxonomyNode"]] = relationship(back_populates="parent")
```

**Step 3: Create `api/src/sorting_hat/models/classification.py`**

```python
import enum
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sorting_hat.models.taxonomy import Base


class StepType(str, enum.Enum):
    scrape = "scrape"
    summarize = "summarize"
    classify = "classify"


class Classification(Base):
    __tablename__ = "classifications"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    url: Mapped[str] = mapped_column(String(2000), nullable=False)
    raw_content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    product_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    primary_node_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("taxonomy_nodes.id"), nullable=True
    )
    secondary_node_ids: Mapped[list[str]] = mapped_column(
        ARRAY(UUID(as_uuid=False)), nullable=False, default=list
    )
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_used: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    model_params: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    reasoning: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    primary_node: Mapped["TaxonomyNode | None"] = relationship(foreign_keys=[primary_node_id])
    steps: Mapped[list["ClassificationStep"]] = relationship(back_populates="classification")


class ClassificationStep(Base):
    __tablename__ = "classification_steps"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    classification_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("classifications.id"), nullable=False
    )
    step_type: Mapped[StepType] = mapped_column(Enum(StepType), nullable=False)
    input_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    output_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    model_used: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    classification: Mapped[Classification] = relationship(back_populates="steps")
```

**Step 4: Create `api/src/sorting_hat/models/__init__.py`**

```python
from sorting_hat.models.taxonomy import Base, Branch, GovernanceGroup, TaxonomyNode
from sorting_hat.models.classification import Classification, ClassificationStep, StepType

__all__ = [
    "Base",
    "Branch",
    "GovernanceGroup",
    "TaxonomyNode",
    "Classification",
    "ClassificationStep",
    "StepType",
]
```

**Step 5: Create the raw SQL migration for Supabase — `supabase/migrations/001_initial_schema.sql`**

```sql
-- Enable ltree extension (Supabase has it available)
CREATE EXTENSION IF NOT EXISTS ltree;

-- Branch enum
CREATE TYPE branch AS ENUM ('software', 'hardware');
CREATE TYPE step_type AS ENUM ('scrape', 'summarize', 'classify');

-- Governance groups
CREATE TABLE governance_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    covers_software BOOLEAN NOT NULL DEFAULT TRUE,
    covers_hardware BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Taxonomy nodes
CREATE TABLE taxonomy_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    governance_group_id UUID NOT NULL REFERENCES governance_groups(id),
    parent_id UUID REFERENCES taxonomy_nodes(id),
    path ltree NOT NULL DEFAULT '',
    name VARCHAR(300) NOT NULL,
    slug VARCHAR(300) NOT NULL,
    level INTEGER NOT NULL,
    branch branch NOT NULL,
    definition TEXT NOT NULL DEFAULT '',
    distinguishing_characteristics TEXT NOT NULL DEFAULT '',
    inclusions TEXT NOT NULL DEFAULT '',
    exclusions TEXT NOT NULL DEFAULT '',
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (parent_id, slug)
);

CREATE INDEX idx_taxonomy_nodes_path ON taxonomy_nodes USING gist (path);
CREATE INDEX idx_taxonomy_nodes_governance_group ON taxonomy_nodes (governance_group_id);
CREATE INDEX idx_taxonomy_nodes_parent ON taxonomy_nodes (parent_id);
CREATE INDEX idx_taxonomy_nodes_branch ON taxonomy_nodes (branch);

-- Classifications
CREATE TABLE classifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url VARCHAR(2000) NOT NULL,
    raw_content TEXT NOT NULL DEFAULT '',
    product_summary TEXT NOT NULL DEFAULT '',
    primary_node_id UUID REFERENCES taxonomy_nodes(id),
    secondary_node_ids UUID[] NOT NULL DEFAULT '{}',
    confidence_score FLOAT,
    model_used VARCHAR(200) NOT NULL DEFAULT '',
    model_params TEXT NOT NULL DEFAULT '{}',
    reasoning TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_classifications_url ON classifications (url);
CREATE INDEX idx_classifications_primary_node ON classifications (primary_node_id);

-- Classification steps
CREATE TABLE classification_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    classification_id UUID NOT NULL REFERENCES classifications(id) ON DELETE CASCADE,
    step_type step_type NOT NULL,
    input_text TEXT NOT NULL DEFAULT '',
    output_text TEXT NOT NULL DEFAULT '',
    model_used VARCHAR(200) NOT NULL DEFAULT '',
    tokens_used INTEGER NOT NULL DEFAULT 0,
    latency_ms INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_classification_steps_classification ON classification_steps (classification_id);

-- Auto-update updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_governance_groups_updated_at
    BEFORE UPDATE ON governance_groups
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_taxonomy_nodes_updated_at
    BEFORE UPDATE ON taxonomy_nodes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

**Step 6: Write model import test — `api/tests/test_models.py`**

```python
def test_models_import():
    from sorting_hat.models import (
        Base,
        Branch,
        GovernanceGroup,
        TaxonomyNode,
        Classification,
        ClassificationStep,
        StepType,
    )

    assert GovernanceGroup.__tablename__ == "governance_groups"
    assert TaxonomyNode.__tablename__ == "taxonomy_nodes"
    assert Classification.__tablename__ == "classifications"
    assert ClassificationStep.__tablename__ == "classification_steps"
    assert Branch.software.value == "software"
    assert StepType.scrape.value == "scrape"
```

**Step 7: Run tests**

```bash
cd api && pytest tests/ -v
```

Expected: Both `test_health_returns_ok` and `test_models_import` pass.

**Step 8: Commit**

```bash
git add api/src/sorting_hat/db.py api/src/sorting_hat/models/ api/tests/test_models.py supabase/
git commit -m "feat: add database models and initial SQL migration"
```

---

## Task 3: Pydantic Schemas

**Files:**
- Create: `api/src/sorting_hat/schemas/__init__.py`
- Create: `api/src/sorting_hat/schemas/taxonomy.py`
- Create: `api/src/sorting_hat/schemas/classification.py`
- Create: `api/tests/test_schemas.py`

**Step 1: Create `api/src/sorting_hat/schemas/taxonomy.py`**

```python
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
```

**Step 2: Create `api/src/sorting_hat/schemas/classification.py`**

```python
from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class ClassifyRequest(BaseModel):
    url: str = Field(..., max_length=2000)
    model: str | None = None
    provider: str | None = None


class ClassificationStepResponse(BaseModel):
    id: str
    step_type: str
    input_text: str
    output_text: str
    model_used: str
    tokens_used: int
    latency_ms: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ClassificationResponse(BaseModel):
    id: str
    url: str
    product_summary: str
    primary_node_id: str | None
    primary_node_path: str | None = None
    secondary_node_ids: list[str]
    confidence_score: float | None
    model_used: str
    reasoning: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ClassificationDetail(ClassificationResponse):
    raw_content: str
    steps: list[ClassificationStepResponse] = []
```

**Step 3: Create `api/src/sorting_hat/schemas/__init__.py`**

```python
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
from sorting_hat.schemas.classification import (
    ClassificationDetail,
    ClassificationResponse,
    ClassificationStepResponse,
    ClassifyRequest,
)

__all__ = [
    "GovernanceGroupCreate",
    "GovernanceGroupResponse",
    "GovernanceGroupUpdate",
    "TaxonomyNodeCreate",
    "TaxonomyNodeDetail",
    "TaxonomyNodeMove",
    "TaxonomyNodeResponse",
    "TaxonomyNodeUpdate",
    "ClassificationDetail",
    "ClassificationResponse",
    "ClassificationStepResponse",
    "ClassifyRequest",
]
```

**Step 4: Write schema tests — `api/tests/test_schemas.py`**

```python
import pytest
from pydantic import ValidationError

from sorting_hat.schemas.taxonomy import (
    GovernanceGroupCreate,
    TaxonomyNodeCreate,
    TaxonomyNodeUpdate,
)
from sorting_hat.schemas.classification import ClassifyRequest


def test_governance_group_create_valid():
    g = GovernanceGroupCreate(name="Security", slug="security", description="Protect things")
    assert g.name == "Security"
    assert g.covers_software is True
    assert g.covers_hardware is False


def test_governance_group_create_requires_name():
    with pytest.raises(ValidationError):
        GovernanceGroupCreate(slug="security")


def test_taxonomy_node_create_valid():
    n = TaxonomyNodeCreate(name="Endpoint Security", slug="endpoint-security", branch="software")
    assert n.parent_id is None
    assert n.definition == ""


def test_taxonomy_node_update_all_optional():
    u = TaxonomyNodeUpdate()
    assert u.name is None
    assert u.definition is None


def test_classify_request_valid():
    r = ClassifyRequest(url="https://example.com/product")
    assert r.model is None
    assert r.provider is None


def test_classify_request_requires_url():
    with pytest.raises(ValidationError):
        ClassifyRequest()
```

**Step 5: Run tests**

```bash
cd api && pytest tests/ -v
```

Expected: All tests pass.

**Step 6: Commit**

```bash
git add api/src/sorting_hat/schemas/ api/tests/test_schemas.py
git commit -m "feat: add Pydantic schemas for taxonomy and classification"
```

---

## Task 4: Taxonomy CRUD Service Layer

**Files:**
- Create: `api/src/sorting_hat/services/__init__.py`
- Create: `api/src/sorting_hat/services/taxonomy.py`
- Create: `api/tests/test_taxonomy_service.py`

**Step 1: Create `api/src/sorting_hat/services/taxonomy.py`**

This is the core business logic for taxonomy management. It operates on SQLAlchemy sessions and enforces tree integrity.

```python
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sorting_hat.models.taxonomy import Branch, GovernanceGroup, TaxonomyNode
from sorting_hat.schemas.taxonomy import (
    GovernanceGroupCreate,
    GovernanceGroupUpdate,
    TaxonomyNodeCreate,
    TaxonomyNodeUpdate,
)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


class TaxonomyServiceError(Exception):
    pass


class TaxonomyService:
    def __init__(self, session: AsyncSession):
        self.session = session

    # --- Governance Groups ---

    async def list_governance_groups(self) -> list[GovernanceGroup]:
        result = await self.session.execute(
            select(GovernanceGroup).order_by(GovernanceGroup.sort_order)
        )
        return list(result.scalars().all())

    async def get_governance_group(self, slug: str) -> GovernanceGroup | None:
        result = await self.session.execute(
            select(GovernanceGroup).where(GovernanceGroup.slug == slug)
        )
        return result.scalar_one_or_none()

    async def create_governance_group(self, data: GovernanceGroupCreate) -> GovernanceGroup:
        group = GovernanceGroup(**data.model_dump())
        self.session.add(group)
        await self.session.flush()
        return group

    async def update_governance_group(
        self, slug: str, data: GovernanceGroupUpdate
    ) -> GovernanceGroup | None:
        group = await self.get_governance_group(slug)
        if not group:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(group, field, value)
        await self.session.flush()
        return group

    async def delete_governance_group(self, slug: str) -> bool:
        group = await self.get_governance_group(slug)
        if not group:
            return False
        # Check for nodes
        result = await self.session.execute(
            select(TaxonomyNode).where(TaxonomyNode.governance_group_id == group.id).limit(1)
        )
        if result.scalar_one_or_none():
            raise TaxonomyServiceError("Cannot delete group with existing nodes")
        await self.session.delete(group)
        await self.session.flush()
        return True

    # --- Taxonomy Nodes ---

    async def get_node(self, node_id: str) -> TaxonomyNode | None:
        result = await self.session.execute(
            select(TaxonomyNode)
            .where(TaxonomyNode.id == node_id)
            .options(selectinload(TaxonomyNode.children))
        )
        return result.scalar_one_or_none()

    async def list_nodes(
        self,
        branch: str | None = None,
        governance_group_slug: str | None = None,
        max_depth: int | None = None,
    ) -> list[TaxonomyNode]:
        query = select(TaxonomyNode).order_by(TaxonomyNode.path, TaxonomyNode.sort_order)
        if branch:
            query = query.where(TaxonomyNode.branch == branch)
        if governance_group_slug:
            query = query.join(GovernanceGroup).where(GovernanceGroup.slug == governance_group_slug)
        if max_depth is not None:
            query = query.where(TaxonomyNode.level <= max_depth)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_node(self, data: TaxonomyNodeCreate) -> TaxonomyNode:
        if data.parent_id:
            parent = await self.get_node(data.parent_id)
            if not parent:
                raise TaxonomyServiceError("Parent node not found")
            if parent.branch.value != data.branch:
                raise TaxonomyServiceError("Node branch must match parent branch")
            level = parent.level + 1
            path = f"{parent.path}.{slugify(data.name)}" if parent.path else slugify(data.name)
            governance_group_id = parent.governance_group_id
        else:
            # Root-level node (level 1 = branch, level 2 = governance group)
            # Must provide governance_group context externally for level-2 nodes
            raise TaxonomyServiceError("Nodes must have a parent (use seed for root nodes)")

        node = TaxonomyNode(
            governance_group_id=governance_group_id,
            parent_id=data.parent_id,
            path=path,
            name=data.name,
            slug=slugify(data.name),
            level=level,
            branch=Branch(data.branch),
            definition=data.definition,
            distinguishing_characteristics=data.distinguishing_characteristics,
            inclusions=data.inclusions,
            exclusions=data.exclusions,
            sort_order=data.sort_order,
        )
        self.session.add(node)
        await self.session.flush()
        return node

    async def update_node(self, node_id: str, data: TaxonomyNodeUpdate) -> TaxonomyNode | None:
        node = await self.get_node(node_id)
        if not node:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(node, field, value)
        await self.session.flush()
        return node

    async def delete_node(self, node_id: str) -> bool:
        node = await self.get_node(node_id)
        if not node:
            return False
        if node.children:
            raise TaxonomyServiceError("Cannot delete node with children — delete leaves first")
        await self.session.delete(node)
        await self.session.flush()
        return True

    async def get_subtree(self, node_id: str) -> list[TaxonomyNode]:
        node = await self.get_node(node_id)
        if not node:
            return []
        # Use path prefix matching (works with ltree-style dot-separated paths)
        result = await self.session.execute(
            select(TaxonomyNode)
            .where(TaxonomyNode.path.like(f"{node.path}%"))
            .order_by(TaxonomyNode.path, TaxonomyNode.sort_order)
        )
        return list(result.scalars().all())

    async def get_parent_chain(self, node_id: str) -> list[TaxonomyNode]:
        chain = []
        node = await self.get_node(node_id)
        while node and node.parent_id:
            result = await self.session.execute(
                select(TaxonomyNode).where(TaxonomyNode.id == node.parent_id)
            )
            node = result.scalar_one_or_none()
            if node:
                chain.insert(0, node)
        return chain

    async def search_nodes(self, query: str) -> list[TaxonomyNode]:
        pattern = f"%{query}%"
        result = await self.session.execute(
            select(TaxonomyNode)
            .where(
                TaxonomyNode.name.ilike(pattern)
                | TaxonomyNode.definition.ilike(pattern)
                | TaxonomyNode.distinguishing_characteristics.ilike(pattern)
            )
            .order_by(TaxonomyNode.path)
            .limit(50)
        )
        return list(result.scalars().all())
```

**Step 2: Create `api/src/sorting_hat/services/__init__.py`**

```python
from sorting_hat.services.taxonomy import TaxonomyService, TaxonomyServiceError

__all__ = ["TaxonomyService", "TaxonomyServiceError"]
```

**Step 3: Write unit tests — `api/tests/test_taxonomy_service.py`**

These tests validate the service logic without a database (testing the slugify helper and import correctness). Full integration tests come after we wire up a test database.

```python
from sorting_hat.services.taxonomy import TaxonomyService, TaxonomyServiceError, slugify


def test_slugify_simple():
    assert slugify("Endpoint Security") == "endpoint_security"


def test_slugify_special_chars():
    assert slugify("CI/CD & Build Automation") == "ci_cd_build_automation"


def test_slugify_dashes_and_parens():
    assert slugify("ETL/ELT Platforms") == "etl_elt_platforms"


def test_slugify_already_clean():
    assert slugify("databases") == "databases"


def test_service_class_exists():
    # Verify the service can be imported and has expected methods
    assert hasattr(TaxonomyService, "list_governance_groups")
    assert hasattr(TaxonomyService, "create_node")
    assert hasattr(TaxonomyService, "delete_node")
    assert hasattr(TaxonomyService, "search_nodes")


def test_service_error_is_exception():
    assert issubclass(TaxonomyServiceError, Exception)
```

**Step 4: Run tests**

```bash
cd api && pytest tests/ -v
```

Expected: All tests pass.

**Step 5: Commit**

```bash
git add api/src/sorting_hat/services/ api/tests/test_taxonomy_service.py
git commit -m "feat: add taxonomy CRUD service layer"
```

---

## Task 5: Taxonomy API Routes

**Files:**
- Create: `api/src/sorting_hat/routes/__init__.py`
- Create: `api/src/sorting_hat/routes/taxonomy.py`
- Modify: `api/src/sorting_hat/main.py` — register router
- Create: `api/tests/test_taxonomy_routes.py`

**Step 1: Create `api/src/sorting_hat/routes/taxonomy.py`**

```python
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
```

**Step 2: Create `api/src/sorting_hat/routes/__init__.py`**

```python
from sorting_hat.routes.taxonomy import router as taxonomy_router

__all__ = ["taxonomy_router"]
```

**Step 3: Update `api/src/sorting_hat/main.py` to register router**

```python
from fastapi import FastAPI

from sorting_hat.config import settings
from sorting_hat.routes import taxonomy_router

app = FastAPI(title="The Sorting Hat", version="0.1.0")

app.include_router(taxonomy_router, prefix=settings.api_prefix)


@app.get("/health")
async def health():
    return {"status": "ok"}
```

**Step 4: Write route tests — `api/tests/test_taxonomy_routes.py`**

These test that routes are registered and return expected status codes. Full integration tests require a database.

```python
from fastapi.testclient import TestClient

from sorting_hat.main import app

client = TestClient(app)


def test_taxonomy_routes_registered():
    routes = [route.path for route in app.routes]
    assert "/api/v1/taxonomy/governance-groups" in routes
    assert "/api/v1/taxonomy/nodes" in routes
    assert "/api/v1/taxonomy/nodes/search" in routes
```

**Step 5: Run tests**

```bash
cd api && pytest tests/ -v
```

Expected: All tests pass.

**Step 6: Commit**

```bash
git add api/src/sorting_hat/routes/ api/src/sorting_hat/main.py api/tests/test_taxonomy_routes.py
git commit -m "feat: add taxonomy management API routes"
```

---

## Task 6: LLM Provider Abstraction

**Files:**
- Create: `api/src/sorting_hat/llm/__init__.py`
- Create: `api/src/sorting_hat/llm/provider.py`
- Create: `api/src/sorting_hat/llm/openai_compat.py`
- Create: `api/tests/test_llm_provider.py`
- Modify: `api/pyproject.toml` — add openai dependency

**Step 1: Add openai to dependencies in `api/pyproject.toml`**

Add `"openai>=1.60.0"` to the `dependencies` list.

**Step 2: Create `api/src/sorting_hat/llm/provider.py`**

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMMessage:
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    content: str
    model: str
    tokens_used: int


class LLMProvider(ABC):
    @abstractmethod
    async def complete(
        self,
        messages: list[LLMMessage],
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        pass
```

**Step 3: Create `api/src/sorting_hat/llm/openai_compat.py`**

This single implementation covers OpenRouter, OpenAI direct, and Ollama — they all use the OpenAI API format.

```python
from openai import AsyncOpenAI

from sorting_hat.llm.provider import LLMMessage, LLMProvider, LLMResponse


class OpenAICompatProvider(LLMProvider):
    def __init__(self, api_key: str, base_url: str | None = None):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def complete(
        self,
        messages: list[LLMMessage],
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choice = response.choices[0]
        tokens = response.usage.total_tokens if response.usage else 0
        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            tokens_used=tokens,
        )
```

**Step 4: Create `api/src/sorting_hat/llm/__init__.py`**

```python
from sorting_hat.llm.provider import LLMMessage, LLMProvider, LLMResponse
from sorting_hat.llm.openai_compat import OpenAICompatProvider

__all__ = ["LLMMessage", "LLMProvider", "LLMResponse", "OpenAICompatProvider"]
```

**Step 5: Add LLM config to `api/src/sorting_hat/config.py`**

Add these fields to the `Settings` class:

```python
    llm_provider: str = "openrouter"  # "openrouter", "openai", "ollama"
    llm_api_key: str = ""
    llm_base_url: str = "https://openrouter.ai/api/v1"
    llm_model: str = "anthropic/claude-sonnet-4-20250514"
```

**Step 6: Write tests — `api/tests/test_llm_provider.py`**

```python
from sorting_hat.llm.provider import LLMMessage, LLMProvider, LLMResponse
from sorting_hat.llm.openai_compat import OpenAICompatProvider


def test_llm_message_creation():
    msg = LLMMessage(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"


def test_llm_response_creation():
    resp = LLMResponse(content="Hi", model="gpt-4", tokens_used=10)
    assert resp.content == "Hi"
    assert resp.tokens_used == 10


def test_openai_compat_provider_is_llm_provider():
    provider = OpenAICompatProvider(api_key="test-key")
    assert isinstance(provider, LLMProvider)


def test_openai_compat_provider_custom_base_url():
    provider = OpenAICompatProvider(
        api_key="test-key", base_url="http://localhost:11434/v1"
    )
    assert provider.client.base_url.host == "localhost"
```

**Step 7: Install new dependency and run tests**

```bash
cd api && pip install -e ".[dev]" && pytest tests/ -v
```

Expected: All tests pass.

**Step 8: Commit**

```bash
git add api/src/sorting_hat/llm/ api/src/sorting_hat/config.py api/pyproject.toml api/tests/test_llm_provider.py
git commit -m "feat: add provider-agnostic LLM abstraction layer"
```

---

## Task 7: Scraper Service

**Files:**
- Create: `api/src/sorting_hat/services/scraper.py`
- Create: `api/tests/test_scraper.py`
- Modify: `api/pyproject.toml` — add trafilatura dependency

**Step 1: Add trafilatura to dependencies in `api/pyproject.toml`**

Add `"trafilatura>=2.0.0"` to the `dependencies` list.

**Step 2: Create `api/src/sorting_hat/services/scraper.py`**

```python
import httpx
import trafilatura


class ScraperError(Exception):
    pass


class Scraper:
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    async def fetch_and_extract(self, url: str) -> tuple[str, str]:
        """Fetch URL and extract main content. Returns (raw_html, extracted_text)."""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout, follow_redirects=True
            ) as client:
                response = await client.get(
                    url,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (compatible; SortingHat/1.0; "
                            "+https://github.com/sorting-hat)"
                        )
                    },
                )
                response.raise_for_status()
                raw_html = response.text
        except httpx.HTTPError as e:
            raise ScraperError(f"Failed to fetch {url}: {e}") from e

        extracted = trafilatura.extract(
            raw_html,
            include_comments=False,
            include_tables=True,
            favor_recall=True,
        )

        if not extracted:
            raise ScraperError(f"Could not extract meaningful content from {url}")

        return raw_html, extracted
```

**Step 3: Write tests — `api/tests/test_scraper.py`**

```python
import pytest
import trafilatura

from sorting_hat.services.scraper import Scraper, ScraperError


def test_scraper_exists():
    scraper = Scraper()
    assert scraper.timeout == 30.0


def test_scraper_custom_timeout():
    scraper = Scraper(timeout=10.0)
    assert scraper.timeout == 10.0


def test_scraper_error_is_exception():
    assert issubclass(ScraperError, Exception)


def test_trafilatura_extracts_content():
    """Verify trafilatura can extract content from a simple HTML page."""
    html = """
    <html>
    <head><title>Test Product</title></head>
    <body>
        <nav>Navigation here</nav>
        <main>
            <h1>Amazing Security Product</h1>
            <p>Our endpoint protection platform defends your devices against
            malware, ransomware, and advanced threats using AI-powered detection.</p>
            <p>Features include real-time scanning, behavioral analysis,
            and automated response capabilities.</p>
        </main>
        <footer>Footer content</footer>
    </body>
    </html>
    """
    result = trafilatura.extract(html, include_comments=False, favor_recall=True)
    assert result is not None
    assert "endpoint protection" in result.lower() or "security" in result.lower()
```

**Step 4: Install and run tests**

```bash
cd api && pip install -e ".[dev]" && pytest tests/ -v
```

Expected: All tests pass.

**Step 5: Commit**

```bash
git add api/src/sorting_hat/services/scraper.py api/tests/test_scraper.py api/pyproject.toml
git commit -m "feat: add URL scraper service with trafilatura extraction"
```

---

## Task 8: Classification Pipeline Service

**Files:**
- Create: `api/src/sorting_hat/services/classifier.py`
- Create: `api/src/sorting_hat/prompts/__init__.py`
- Create: `api/src/sorting_hat/prompts/summarize.py`
- Create: `api/src/sorting_hat/prompts/classify.py`
- Create: `api/tests/test_classifier.py`

**Step 1: Create `api/src/sorting_hat/prompts/summarize.py`**

```python
SUMMARIZE_SYSTEM = """You are a product analyst. Given the content from a product's website, create a structured summary of what the product does.

Your summary must include:
1. **Product Name**: The name of the product
2. **Primary Function**: What the product does in 1-2 sentences
3. **Key Capabilities**: A bulleted list of the product's main features and capabilities
4. **Target Users**: Who uses this product (e.g., developers, IT admins, marketers)
5. **Category Signals**: Any keywords or phrases that indicate what category this product falls into

Be factual. Only include information present in the source content. Do not infer or guess."""

SUMMARIZE_USER = """Analyze the following product webpage content and create a structured summary:

---
{content}
---

Provide the structured summary as described."""
```

**Step 2: Create `api/src/sorting_hat/prompts/classify.py`**

```python
CLASSIFY_SYSTEM = """You are an enterprise IT product classifier. Given a product summary and a taxonomy of categories with definitions, classify the product.

Rules:
- Assign exactly ONE primary category. This determines which governance team owns the product.
- Assign up to TWO secondary categories for cross-functional visibility. Secondary is optional.
- Classify by what the product DOES (capability), not how it's delivered (SaaS vs on-prem is irrelevant).
- Primary = "Which governance team owns the standard, evaluation, and lifecycle?"
- Secondary = "Which other governance teams have a legitimate interest or need visibility?"

Respond in this exact JSON format:
{{
    "primary": {{
        "node_id": "<uuid>",
        "node_path": "<full path like Software > Security > Endpoint Security>",
        "reasoning": "<why this is the primary category>"
    }},
    "secondaries": [
        {{
            "node_id": "<uuid>",
            "node_path": "<full path>",
            "reasoning": "<why this team needs visibility>"
        }}
    ],
    "confidence": <float 0.0-1.0>
}}"""

CLASSIFY_USER = """## Product Summary

{summary}

## Taxonomy

{taxonomy}

Classify this product into the taxonomy. Return JSON only."""
```

**Step 3: Create `api/src/sorting_hat/prompts/__init__.py`**

```python
from sorting_hat.prompts.summarize import SUMMARIZE_SYSTEM, SUMMARIZE_USER
from sorting_hat.prompts.classify import CLASSIFY_SYSTEM, CLASSIFY_USER

__all__ = ["SUMMARIZE_SYSTEM", "SUMMARIZE_USER", "CLASSIFY_SYSTEM", "CLASSIFY_USER"]
```

**Step 4: Create `api/src/sorting_hat/services/classifier.py`**

```python
import json
import time
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from sorting_hat.llm.provider import LLMMessage, LLMProvider
from sorting_hat.models.classification import Classification, ClassificationStep, StepType
from sorting_hat.models.taxonomy import TaxonomyNode
from sorting_hat.prompts import CLASSIFY_SYSTEM, CLASSIFY_USER, SUMMARIZE_SYSTEM, SUMMARIZE_USER
from sorting_hat.services.scraper import Scraper
from sorting_hat.services.taxonomy import TaxonomyService


class ClassificationError(Exception):
    pass


@dataclass
class ClassificationResult:
    classification: Classification
    steps: list[ClassificationStep]


class ClassifierService:
    def __init__(
        self,
        session: AsyncSession,
        llm: LLMProvider,
        model: str,
        scraper: Scraper | None = None,
    ):
        self.session = session
        self.llm = llm
        self.model = model
        self.scraper = scraper or Scraper()
        self.taxonomy_service = TaxonomyService(session)

    async def classify_url(self, url: str) -> ClassificationResult:
        classification = Classification(url=url)
        self.session.add(classification)
        steps = []

        # Step 1: Scrape
        start = time.monotonic()
        raw_html, extracted_text = await self.scraper.fetch_and_extract(url)
        scrape_ms = int((time.monotonic() - start) * 1000)

        classification.raw_content = extracted_text
        scrape_step = ClassificationStep(
            classification_id=classification.id,
            step_type=StepType.scrape,
            input_text=url,
            output_text=extracted_text[:10000],
            latency_ms=scrape_ms,
        )
        self.session.add(scrape_step)
        steps.append(scrape_step)

        # Step 2: Summarize
        start = time.monotonic()
        summary_response = await self.llm.complete(
            messages=[
                LLMMessage(role="system", content=SUMMARIZE_SYSTEM),
                LLMMessage(role="user", content=SUMMARIZE_USER.format(content=extracted_text[:8000])),
            ],
            model=self.model,
        )
        summarize_ms = int((time.monotonic() - start) * 1000)

        classification.product_summary = summary_response.content
        summarize_step = ClassificationStep(
            classification_id=classification.id,
            step_type=StepType.summarize,
            input_text=extracted_text[:10000],
            output_text=summary_response.content,
            model_used=summary_response.model,
            tokens_used=summary_response.tokens_used,
            latency_ms=summarize_ms,
        )
        self.session.add(summarize_step)
        steps.append(summarize_step)

        # Step 3: Classify
        taxonomy_text = await self._build_taxonomy_text()

        start = time.monotonic()
        classify_response = await self.llm.complete(
            messages=[
                LLMMessage(role="system", content=CLASSIFY_SYSTEM),
                LLMMessage(
                    role="user",
                    content=CLASSIFY_USER.format(
                        summary=summary_response.content, taxonomy=taxonomy_text
                    ),
                ),
            ],
            model=self.model,
        )
        classify_ms = int((time.monotonic() - start) * 1000)

        classify_step = ClassificationStep(
            classification_id=classification.id,
            step_type=StepType.classify,
            input_text=summary_response.content,
            output_text=classify_response.content,
            model_used=classify_response.model,
            tokens_used=classify_response.tokens_used,
            latency_ms=classify_ms,
        )
        self.session.add(classify_step)
        steps.append(classify_step)

        # Parse classification result
        parsed = self._parse_classification(classify_response.content)
        classification.primary_node_id = parsed.get("primary_node_id")
        classification.secondary_node_ids = parsed.get("secondary_node_ids", [])
        classification.confidence_score = parsed.get("confidence")
        classification.model_used = classify_response.model
        classification.reasoning = parsed.get("reasoning", "")

        await self.session.flush()
        return ClassificationResult(classification=classification, steps=steps)

    async def _build_taxonomy_text(self) -> str:
        nodes = await self.taxonomy_service.list_nodes()
        lines = []
        for node in nodes:
            indent = "  " * (node.level - 1)
            line = f"{indent}- [{node.id}] {node.name}"
            if node.definition:
                line += f": {node.definition}"
            lines.append(line)
        return "\n".join(lines)

    def _parse_classification(self, raw: str) -> dict:
        try:
            # Strip markdown code fences if present
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = "\n".join(cleaned.split("\n")[1:])
            if cleaned.endswith("```"):
                cleaned = "\n".join(cleaned.split("\n")[:-1])
            data = json.loads(cleaned)

            result = {}
            if "primary" in data and "node_id" in data["primary"]:
                result["primary_node_id"] = data["primary"]["node_id"]
                result["reasoning"] = data["primary"].get("reasoning", "")
            result["secondary_node_ids"] = [
                s["node_id"] for s in data.get("secondaries", []) if "node_id" in s
            ][:2]
            result["confidence"] = data.get("confidence")
            return result
        except (json.JSONDecodeError, KeyError, TypeError):
            return {"reasoning": f"Failed to parse LLM response: {raw[:500]}"}
```

**Step 5: Write tests — `api/tests/test_classifier.py`**

```python
from sorting_hat.services.classifier import ClassifierService, ClassificationError
from sorting_hat.prompts import SUMMARIZE_SYSTEM, CLASSIFY_SYSTEM


def test_classifier_service_exists():
    assert hasattr(ClassifierService, "classify_url")


def test_parse_classification_valid():
    raw = '''```json
{
    "primary": {
        "node_id": "abc-123",
        "node_path": "Software > Security > Endpoint Security",
        "reasoning": "This is an endpoint protection product"
    },
    "secondaries": [
        {
            "node_id": "def-456",
            "node_path": "Software > IT Ops > Monitoring",
            "reasoning": "Has monitoring features"
        }
    ],
    "confidence": 0.92
}
```'''
    # Test the static parsing method
    service = ClassifierService.__new__(ClassifierService)
    result = service._parse_classification(raw)
    assert result["primary_node_id"] == "abc-123"
    assert result["secondary_node_ids"] == ["def-456"]
    assert result["confidence"] == 0.92
    assert "endpoint protection" in result["reasoning"]


def test_parse_classification_invalid_json():
    service = ClassifierService.__new__(ClassifierService)
    result = service._parse_classification("not json at all")
    assert "Failed to parse" in result["reasoning"]


def test_parse_classification_max_two_secondaries():
    raw = json.dumps({
        "primary": {"node_id": "a", "reasoning": "test"},
        "secondaries": [
            {"node_id": "b"},
            {"node_id": "c"},
            {"node_id": "d"},
        ],
        "confidence": 0.8,
    })
    service = ClassifierService.__new__(ClassifierService)
    result = service._parse_classification(raw)
    assert len(result["secondary_node_ids"]) == 2


def test_prompts_are_nonempty():
    assert len(SUMMARIZE_SYSTEM) > 50
    assert "{content}" in SUMMARIZE_USER
    assert len(CLASSIFY_SYSTEM) > 50
    assert "{summary}" in CLASSIFY_USER
    assert "{taxonomy}" in CLASSIFY_USER


# Need this import for test_parse_classification_max_two_secondaries
import json
from sorting_hat.prompts.summarize import SUMMARIZE_USER
from sorting_hat.prompts.classify import CLASSIFY_USER
```

**Step 6: Run tests**

```bash
cd api && pytest tests/ -v
```

Expected: All tests pass.

**Step 7: Commit**

```bash
git add api/src/sorting_hat/services/classifier.py api/src/sorting_hat/prompts/ api/tests/test_classifier.py
git commit -m "feat: add classification pipeline with scrape/summarize/classify steps"
```

---

## Task 9: Classification API Routes

**Files:**
- Create: `api/src/sorting_hat/routes/classification.py`
- Modify: `api/src/sorting_hat/routes/__init__.py` — add classification router
- Modify: `api/src/sorting_hat/main.py` — register classification router
- Create: `api/tests/test_classification_routes.py`

**Step 1: Create `api/src/sorting_hat/routes/classification.py`**

```python
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
```

**Step 2: Update `api/src/sorting_hat/routes/__init__.py`**

```python
from sorting_hat.routes.taxonomy import router as taxonomy_router
from sorting_hat.routes.classification import router as classification_router

__all__ = ["taxonomy_router", "classification_router"]
```

**Step 3: Update `api/src/sorting_hat/main.py`**

```python
from fastapi import FastAPI

from sorting_hat.config import settings
from sorting_hat.routes import taxonomy_router, classification_router

app = FastAPI(title="The Sorting Hat", version="0.1.0")

app.include_router(taxonomy_router, prefix=settings.api_prefix)
app.include_router(classification_router, prefix=settings.api_prefix)


@app.get("/health")
async def health():
    return {"status": "ok"}
```

**Step 4: Write route tests — `api/tests/test_classification_routes.py`**

```python
from fastapi.testclient import TestClient

from sorting_hat.main import app

client = TestClient(app)


def test_classification_routes_registered():
    routes = [route.path for route in app.routes]
    assert "/api/v1/classify" in routes
    assert "/api/v1/classify/{classification_id}" in routes
```

**Step 5: Run tests**

```bash
cd api && pytest tests/ -v
```

Expected: All tests pass.

**Step 6: Commit**

```bash
git add api/src/sorting_hat/routes/ api/src/sorting_hat/main.py api/tests/test_classification_routes.py
git commit -m "feat: add classification API routes"
```

---

## Task 10: Taxonomy Seed Data

**Files:**
- Create: `api/src/sorting_hat/seed.py`
- Create: `api/tests/test_seed.py`

**Step 1: Create `api/src/sorting_hat/seed.py`**

This script parses the research docs and generates seed data. It's a standalone script that produces SQL INSERT statements.

```python
"""Parse taxonomy research docs and generate seed SQL for the initial taxonomy data.

Usage: python -m sorting_hat.seed > supabase/migrations/002_seed_taxonomy.sql
"""

import re
import sys
from uuid import uuid5, NAMESPACE_DNS


# Deterministic UUIDs so seeds are idempotent
def make_id(name: str) -> str:
    return str(uuid5(NAMESPACE_DNS, f"sorting-hat.{name}"))


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def escape_sql(text: str) -> str:
    return text.replace("'", "''")


GOVERNANCE_GROUPS = [
    {
        "name": "Application Development & Platform",
        "slug": "application-development-platform",
        "description": "Building, testing, deploying, and maintaining software; developer tools and platforms",
        "covers_software": True,
        "covers_hardware": False,
        "sort_order": 1,
    },
    {
        "name": "Business Operations",
        "slug": "business-operations",
        "description": "Back-office systems: ERP, finance, HR, procurement, supply chain, legal, compliance",
        "covers_software": True,
        "covers_hardware": False,
        "sort_order": 2,
    },
    {
        "name": "Customer & Revenue Technology",
        "slug": "customer-revenue-technology",
        "description": "Front-office systems: CRM, marketing, sales enablement, e-commerce, customer success",
        "covers_software": True,
        "covers_hardware": False,
        "sort_order": 3,
    },
    {
        "name": "Data & Analytics",
        "slug": "data-analytics",
        "description": "Collecting, storing, processing, analyzing, and visualizing data; AI/ML platforms",
        "covers_software": True,
        "covers_hardware": False,
        "sort_order": 4,
    },
    {
        "name": "Collaboration & Communication",
        "slug": "collaboration-communication",
        "description": "Enabling people to work together and communicate, both software and physical devices",
        "covers_software": True,
        "covers_hardware": True,
        "sort_order": 5,
    },
    {
        "name": "End-User Computing",
        "slug": "end-user-computing",
        "description": "Individual productivity software and personal work devices",
        "covers_software": True,
        "covers_hardware": True,
        "sort_order": 6,
    },
    {
        "name": "Security",
        "slug": "security",
        "description": "Protecting information, systems, and infrastructure from threats",
        "covers_software": True,
        "covers_hardware": True,
        "sort_order": 7,
    },
    {
        "name": "IT Operations & Infrastructure",
        "slug": "it-operations-infrastructure",
        "description": "Managing, monitoring, and maintaining IT systems; compute and storage hardware",
        "covers_software": True,
        "covers_hardware": True,
        "sort_order": 8,
    },
    {
        "name": "Engineering & Design",
        "slug": "engineering-design",
        "description": "Specialized tools for engineering, manufacturing, design, and media production",
        "covers_software": True,
        "covers_hardware": False,
        "sort_order": 9,
    },
    {
        "name": "Networking",
        "slug": "networking",
        "description": "Connecting systems, managing network infrastructure, enabling device communication",
        "covers_software": True,
        "covers_hardware": True,
        "sort_order": 10,
    },
]


def generate_governance_groups_sql() -> list[str]:
    statements = []
    for g in GOVERNANCE_GROUPS:
        gid = make_id(g["slug"])
        statements.append(
            f"INSERT INTO governance_groups (id, name, slug, description, covers_software, covers_hardware, sort_order) "
            f"VALUES ('{gid}', '{escape_sql(g['name'])}', '{g['slug']}', "
            f"'{escape_sql(g['description'])}', {str(g['covers_software']).upper()}, "
            f"{str(g['covers_hardware']).upper()}, {g['sort_order']});"
        )
    return statements


def main():
    print("-- Sorting Hat: Taxonomy Seed Data")
    print("-- Generated by sorting_hat.seed")
    print()
    print("-- Governance Groups")
    for stmt in generate_governance_groups_sql():
        print(stmt)
    print()
    print("-- NOTE: Full taxonomy node seeding is handled by the seed management command.")
    print("-- Run: python -m sorting_hat.seed_nodes to populate all ~220 taxonomy nodes.")


if __name__ == "__main__":
    main()
```

**Step 2: Write tests — `api/tests/test_seed.py`**

```python
from sorting_hat.seed import make_id, slugify, escape_sql, GOVERNANCE_GROUPS, generate_governance_groups_sql


def test_make_id_deterministic():
    id1 = make_id("security")
    id2 = make_id("security")
    assert id1 == id2


def test_make_id_unique_per_name():
    id1 = make_id("security")
    id2 = make_id("networking")
    assert id1 != id2


def test_slugify():
    assert slugify("Application Development & Platform") == "application_development_platform"


def test_escape_sql():
    assert escape_sql("it's") == "it''s"


def test_governance_groups_count():
    assert len(GOVERNANCE_GROUPS) == 10


def test_generate_sql_produces_10_inserts():
    stmts = generate_governance_groups_sql()
    assert len(stmts) == 10
    assert all("INSERT INTO governance_groups" in s for s in stmts)
```

**Step 3: Run tests**

```bash
cd api && pytest tests/ -v
```

Expected: All tests pass.

**Step 4: Generate the seed SQL**

```bash
cd api && python -m sorting_hat.seed > ../supabase/migrations/002_seed_governance_groups.sql
```

**Step 5: Commit**

```bash
git add api/src/sorting_hat/seed.py api/tests/test_seed.py supabase/migrations/002_seed_governance_groups.sql
git commit -m "feat: add taxonomy seed data generator for governance groups"
```

---

## Task 11: Next.js Project Scaffolding

**Files:**
- Create: `web/` (via `create-next-app`)
- Modify: `web/package.json` — verify dependencies
- Modify: `web/.env.local.example`

**Step 1: Create Next.js app**

```bash
cd /Users/joemc3/tmp/sorting-hat && npx create-next-app@latest web --typescript --tailwind --eslint --app --src-dir --no-import-alias --turbopack
```

Answer prompts: No to import alias.

**Step 2: Create `.env.local.example`**

Create `web/.env.local.example`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

**Step 3: Verify it runs**

```bash
cd web && npm run dev &
sleep 5 && curl -s http://localhost:3000 | head -20
kill %1
```

**Step 4: Commit**

```bash
git add web/
git commit -m "feat: scaffold Next.js app with Tailwind CSS"
```

---

## Task 12: Install shadcn/ui & Core Layout

**Files:**
- Modify: `web/` — shadcn init
- Create: `web/src/app/layout.tsx` (modify)
- Create: `web/src/components/sidebar.tsx`
- Create: `web/src/app/taxonomy/page.tsx`
- Create: `web/src/app/classify/page.tsx`

**Step 1: Initialize shadcn/ui**

```bash
cd web && npx shadcn@latest init -d
```

**Step 2: Add core shadcn components**

```bash
cd web && npx shadcn@latest add button input card badge scroll-area separator sheet tabs
```

**Step 3: Create sidebar — `web/src/components/sidebar.tsx`**

```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/taxonomy", label: "Taxonomy", icon: "🌳" },
  { href: "/classify", label: "Classify", icon: "🔍" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r bg-muted/40 p-4 flex flex-col gap-2">
      <div className="mb-6">
        <h1 className="text-lg font-semibold">The Sorting Hat</h1>
        <p className="text-sm text-muted-foreground">IT Product Taxonomy</p>
      </div>
      <nav className="flex flex-col gap-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
              pathname.startsWith(item.href)
                ? "bg-primary text-primary-foreground"
                : "hover:bg-muted"
            )}
          >
            <span>{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
```

**Step 4: Update layout — `web/src/app/layout.tsx`**

```tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "The Sorting Hat",
  description: "Enterprise IT Product Taxonomy & Classification",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex h-screen">
          <Sidebar />
          <main className="flex-1 overflow-auto p-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
```

**Step 5: Create taxonomy page — `web/src/app/taxonomy/page.tsx`**

```tsx
export default function TaxonomyPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Taxonomy Browser</h2>
      <p className="text-muted-foreground">Taxonomy tree will render here.</p>
    </div>
  );
}
```

**Step 6: Create classify page — `web/src/app/classify/page.tsx`**

```tsx
export default function ClassifyPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Classify a Product</h2>
      <p className="text-muted-foreground">Classification interface will render here.</p>
    </div>
  );
}
```

**Step 7: Update home page — `web/src/app/page.tsx`**

```tsx
import { redirect } from "next/navigation";

export default function Home() {
  redirect("/taxonomy");
}
```

**Step 8: Verify it builds**

```bash
cd web && npm run build
```

Expected: Build succeeds.

**Step 9: Commit**

```bash
git add web/
git commit -m "feat: add shadcn/ui, sidebar layout, and page shells"
```

---

## Task 13: API Client & Taxonomy Tree Component

**Files:**
- Create: `web/src/lib/api.ts`
- Create: `web/src/components/taxonomy-tree.tsx`
- Create: `web/src/components/node-detail.tsx`
- Modify: `web/src/app/taxonomy/page.tsx`

**Step 1: Create API client — `web/src/lib/api.ts`**

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

export interface GovernanceGroup {
  id: string;
  name: string;
  slug: string;
  description: string;
  covers_software: boolean;
  covers_hardware: boolean;
  sort_order: number;
}

export interface TaxonomyNode {
  id: string;
  governance_group_id: string;
  parent_id: string | null;
  path: string;
  name: string;
  slug: string;
  level: number;
  branch: "software" | "hardware";
  definition: string;
  distinguishing_characteristics: string;
  inclusions: string;
  exclusions: string;
  sort_order: number;
}

export interface TaxonomyNodeDetail extends TaxonomyNode {
  children: TaxonomyNode[];
  parent_chain: TaxonomyNode[];
}

export interface ClassificationResult {
  id: string;
  url: string;
  product_summary: string;
  primary_node_id: string | null;
  primary_node_path: string | null;
  secondary_node_ids: string[];
  confidence_score: number | null;
  model_used: string;
  reasoning: string;
  created_at: string;
}

export interface ClassificationStep {
  id: string;
  step_type: "scrape" | "summarize" | "classify";
  input_text: string;
  output_text: string;
  model_used: string;
  tokens_used: number;
  latency_ms: number;
}

export interface ClassificationDetail extends ClassificationResult {
  raw_content: string;
  steps: ClassificationStep[];
}

export const api = {
  taxonomy: {
    listGroups: () => fetchAPI<GovernanceGroup[]>("/taxonomy/governance-groups"),
    listNodes: (params?: { branch?: string; governance_group?: string }) => {
      const query = new URLSearchParams();
      if (params?.branch) query.set("branch", params.branch);
      if (params?.governance_group) query.set("governance_group", params.governance_group);
      const qs = query.toString();
      return fetchAPI<TaxonomyNode[]>(`/taxonomy/nodes${qs ? `?${qs}` : ""}`);
    },
    getNode: (id: string) => fetchAPI<TaxonomyNodeDetail>(`/taxonomy/nodes/${id}`),
    searchNodes: (q: string) => fetchAPI<TaxonomyNode[]>(`/taxonomy/nodes/search?q=${encodeURIComponent(q)}`),
  },
  classify: {
    submit: (url: string, model?: string) =>
      fetchAPI<ClassificationResult>("/classify", {
        method: "POST",
        body: JSON.stringify({ url, model }),
      }),
    get: (id: string) => fetchAPI<ClassificationDetail>(`/classify/${id}`),
    list: (params?: { url?: string; limit?: number; offset?: number }) => {
      const query = new URLSearchParams();
      if (params?.url) query.set("url", params.url);
      if (params?.limit) query.set("limit", String(params.limit));
      if (params?.offset) query.set("offset", String(params.offset));
      const qs = query.toString();
      return fetchAPI<ClassificationResult[]>(`/classify${qs ? `?${qs}` : ""}`);
    },
  },
};
```

**Step 2: Create taxonomy tree component — `web/src/components/taxonomy-tree.tsx`**

```tsx
"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import type { TaxonomyNode } from "@/lib/api";

interface TreeNodeProps {
  node: TaxonomyNode;
  childrenMap: Map<string | null, TaxonomyNode[]>;
  selectedId: string | null;
  onSelect: (node: TaxonomyNode) => void;
}

function TreeNode({ node, childrenMap, selectedId, onSelect }: TreeNodeProps) {
  const [expanded, setExpanded] = useState(node.level <= 2);
  const children = childrenMap.get(node.id) || [];
  const hasChildren = children.length > 0;

  return (
    <div>
      <button
        onClick={() => {
          onSelect(node);
          if (hasChildren) setExpanded(!expanded);
        }}
        className={cn(
          "flex items-center gap-1 w-full text-left px-2 py-1 rounded text-sm hover:bg-muted transition-colors",
          selectedId === node.id && "bg-primary/10 text-primary font-medium"
        )}
        style={{ paddingLeft: `${(node.level - 1) * 16 + 8}px` }}
      >
        {hasChildren && (
          <span className="w-4 text-xs text-muted-foreground">
            {expanded ? "▼" : "▶"}
          </span>
        )}
        {!hasChildren && <span className="w-4" />}
        <span>{node.name}</span>
      </button>
      {expanded &&
        children.map((child) => (
          <TreeNode
            key={child.id}
            node={child}
            childrenMap={childrenMap}
            selectedId={selectedId}
            onSelect={onSelect}
          />
        ))}
    </div>
  );
}

interface TaxonomyTreeProps {
  nodes: TaxonomyNode[];
  selectedId: string | null;
  onSelect: (node: TaxonomyNode) => void;
}

export function TaxonomyTree({ nodes, selectedId, onSelect }: TaxonomyTreeProps) {
  const childrenMap = new Map<string | null, TaxonomyNode[]>();
  for (const node of nodes) {
    const parentId = node.parent_id;
    if (!childrenMap.has(parentId)) childrenMap.set(parentId, []);
    childrenMap.get(parentId)!.push(node);
  }

  const rootNodes = childrenMap.get(null) || [];

  return (
    <div className="space-y-0.5">
      {rootNodes.map((node) => (
        <TreeNode
          key={node.id}
          node={node}
          childrenMap={childrenMap}
          selectedId={selectedId}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}
```

**Step 3: Create node detail panel — `web/src/components/node-detail.tsx`**

```tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import type { TaxonomyNodeDetail } from "@/lib/api";

interface NodeDetailProps {
  node: TaxonomyNodeDetail;
}

export function NodeDetail({ node }: NodeDetailProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
          {node.parent_chain.map((p, i) => (
            <span key={p.id}>
              {i > 0 && " > "}
              {p.name}
            </span>
          ))}
          {node.parent_chain.length > 0 && " > "}
        </div>
        <CardTitle className="flex items-center gap-2">
          {node.name}
          <Badge variant={node.branch === "software" ? "default" : "secondary"}>
            {node.branch}
          </Badge>
          <Badge variant="outline">Level {node.level}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {node.definition && (
          <div>
            <h4 className="font-medium text-sm mb-1">Definition</h4>
            <p className="text-sm text-muted-foreground">{node.definition}</p>
          </div>
        )}
        {node.distinguishing_characteristics && (
          <div>
            <h4 className="font-medium text-sm mb-1">Distinguishing Characteristics</h4>
            <p className="text-sm text-muted-foreground">
              {node.distinguishing_characteristics}
            </p>
          </div>
        )}
        {node.inclusions && (
          <div>
            <h4 className="font-medium text-sm mb-1">Includes</h4>
            <p className="text-sm text-muted-foreground">{node.inclusions}</p>
          </div>
        )}
        {node.exclusions && (
          <div>
            <h4 className="font-medium text-sm mb-1">Does Not Include</h4>
            <p className="text-sm text-muted-foreground">{node.exclusions}</p>
          </div>
        )}
        {node.children.length > 0 && (
          <>
            <Separator />
            <div>
              <h4 className="font-medium text-sm mb-2">
                Children ({node.children.length})
              </h4>
              <div className="flex flex-wrap gap-1">
                {node.children.map((child) => (
                  <Badge key={child.id} variant="outline">
                    {child.name}
                  </Badge>
                ))}
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
```

**Step 4: Update taxonomy page — `web/src/app/taxonomy/page.tsx`**

```tsx
"use client";

import { useEffect, useState } from "react";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { TaxonomyTree } from "@/components/taxonomy-tree";
import { NodeDetail } from "@/components/node-detail";
import { api, type TaxonomyNode, type TaxonomyNodeDetail } from "@/lib/api";

export default function TaxonomyPage() {
  const [nodes, setNodes] = useState<TaxonomyNode[]>([]);
  const [selectedNode, setSelectedNode] = useState<TaxonomyNodeDetail | null>(null);
  const [branch, setBranch] = useState<string>("software");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const fetchNodes = search
      ? api.taxonomy.searchNodes(search)
      : api.taxonomy.listNodes({ branch });
    fetchNodes.then(setNodes).finally(() => setLoading(false));
  }, [branch, search]);

  const handleSelect = async (node: TaxonomyNode) => {
    const detail = await api.taxonomy.getNode(node.id);
    setSelectedNode(detail);
  };

  return (
    <div className="flex gap-6 h-full">
      <div className="w-96 flex flex-col gap-4">
        <h2 className="text-2xl font-bold">Taxonomy</h2>
        <Input
          placeholder="Search nodes..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <Tabs value={branch} onValueChange={setBranch}>
          <TabsList className="w-full">
            <TabsTrigger value="software" className="flex-1">Software</TabsTrigger>
            <TabsTrigger value="hardware" className="flex-1">Hardware</TabsTrigger>
          </TabsList>
        </Tabs>
        <ScrollArea className="flex-1">
          {loading ? (
            <p className="text-sm text-muted-foreground p-2">Loading...</p>
          ) : (
            <TaxonomyTree
              nodes={nodes}
              selectedId={selectedNode?.id ?? null}
              onSelect={handleSelect}
            />
          )}
        </ScrollArea>
      </div>
      <div className="flex-1">
        {selectedNode ? (
          <NodeDetail node={selectedNode} />
        ) : (
          <p className="text-muted-foreground">Select a node to view details.</p>
        )}
      </div>
    </div>
  );
}
```

**Step 5: Verify it builds**

```bash
cd web && npm run build
```

Expected: Build succeeds.

**Step 6: Commit**

```bash
git add web/
git commit -m "feat: add API client, taxonomy tree component, and node detail panel"
```

---

## Task 14: Classification UI

**Files:**
- Create: `web/src/components/classify-form.tsx`
- Create: `web/src/components/classification-result.tsx`
- Modify: `web/src/app/classify/page.tsx`

**Step 1: Create classify form — `web/src/components/classify-form.tsx`**

```tsx
"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface ClassifyFormProps {
  onSubmit: (url: string) => void;
  loading: boolean;
}

export function ClassifyForm({ onSubmit, loading }: ClassifyFormProps) {
  const [url, setUrl] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) onSubmit(url.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <Input
        type="url"
        placeholder="https://example.com/product"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        className="flex-1"
        required
      />
      <Button type="submit" disabled={loading || !url.trim()}>
        {loading ? "Classifying..." : "Classify"}
      </Button>
    </form>
  );
}
```

**Step 2: Create classification result component — `web/src/components/classification-result.tsx`**

```tsx
"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import type { ClassificationDetail } from "@/lib/api";

interface ClassificationResultProps {
  result: ClassificationDetail;
}

export function ClassificationResult({ result }: ClassificationResultProps) {
  const [showSteps, setShowSteps] = useState(false);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Classification Result</CardTitle>
        <p className="text-sm text-muted-foreground">{result.url}</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h4 className="font-medium text-sm mb-1">Product Summary</h4>
          <p className="text-sm text-muted-foreground whitespace-pre-wrap">
            {result.product_summary}
          </p>
        </div>

        <Separator />

        <div>
          <h4 className="font-medium text-sm mb-2">Primary Classification</h4>
          {result.primary_node_path ? (
            <Badge>{result.primary_node_path}</Badge>
          ) : (
            <p className="text-sm text-muted-foreground">No classification</p>
          )}
        </div>

        {result.secondary_node_ids.length > 0 && (
          <div>
            <h4 className="font-medium text-sm mb-2">Secondary Classifications</h4>
            <div className="flex gap-1">
              {result.secondary_node_ids.map((id) => (
                <Badge key={id} variant="outline">{id}</Badge>
              ))}
            </div>
          </div>
        )}

        {result.confidence_score !== null && (
          <div>
            <h4 className="font-medium text-sm mb-1">Confidence</h4>
            <p className="text-sm">{(result.confidence_score * 100).toFixed(0)}%</p>
          </div>
        )}

        {result.reasoning && (
          <div>
            <h4 className="font-medium text-sm mb-1">Reasoning</h4>
            <p className="text-sm text-muted-foreground">{result.reasoning}</p>
          </div>
        )}

        <Separator />

        <button
          onClick={() => setShowSteps(!showSteps)}
          className="text-sm text-primary hover:underline"
        >
          {showSteps ? "Hide" : "Show"} pipeline details ({result.steps.length} steps)
        </button>

        {showSteps && (
          <div className="space-y-3">
            {result.steps.map((step) => (
              <Card key={step.id}>
                <CardContent className="pt-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant="outline">{step.step_type}</Badge>
                    <span className="text-xs text-muted-foreground">
                      {step.latency_ms}ms
                      {step.tokens_used > 0 && ` · ${step.tokens_used} tokens`}
                      {step.model_used && ` · ${step.model_used}`}
                    </span>
                  </div>
                  <pre className="text-xs bg-muted p-2 rounded overflow-auto max-h-48">
                    {step.output_text.slice(0, 2000)}
                  </pre>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

**Step 3: Update classify page — `web/src/app/classify/page.tsx`**

```tsx
"use client";

import { useState } from "react";
import { ClassifyForm } from "@/components/classify-form";
import { ClassificationResult } from "@/components/classification-result";
import { api, type ClassificationDetail } from "@/lib/api";

export default function ClassifyPage() {
  const [result, setResult] = useState<ClassificationDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleClassify = async (url: string) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const classification = await api.classify.submit(url);
      const detail = await api.classify.get(classification.id);
      setResult(detail);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Classification failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl space-y-6">
      <h2 className="text-2xl font-bold">Classify a Product</h2>
      <p className="text-muted-foreground">
        Paste a product URL to classify it into the taxonomy.
      </p>
      <ClassifyForm onSubmit={handleClassify} loading={loading} />
      {error && (
        <div className="text-sm text-destructive bg-destructive/10 p-3 rounded">
          {error}
        </div>
      )}
      {result && <ClassificationResult result={result} />}
    </div>
  );
}
```

**Step 4: Verify it builds**

```bash
cd web && npm run build
```

Expected: Build succeeds.

**Step 5: Commit**

```bash
git add web/
git commit -m "feat: add classification UI with form, result display, and pipeline details"
```

---

## Task 15: CORS, Environment Config & Integration Wiring

**Files:**
- Modify: `api/src/sorting_hat/main.py` — add CORS
- Modify: `api/src/sorting_hat/config.py` — add CORS origins
- Create: `api/.env.example`
- Create: `web/.env.local.example` (update)
- Modify: `.gitignore` — add Python-specific ignores
- Create: `api/src/sorting_hat/main.py` — add lifespan for DB

**Step 1: Add CORS to `api/src/sorting_hat/config.py`**

Add to Settings class:

```python
    cors_origins: list[str] = ["http://localhost:3000"]
```

**Step 2: Update `api/src/sorting_hat/main.py`**

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sorting_hat.config import settings
from sorting_hat.routes import taxonomy_router, classification_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="The Sorting Hat", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(taxonomy_router, prefix=settings.api_prefix)
app.include_router(classification_router, prefix=settings.api_prefix)


@app.get("/health")
async def health():
    return {"status": "ok"}
```

**Step 3: Create `api/.env.example`**

```
SORTING_HAT_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:54322/postgres
SORTING_HAT_LLM_API_KEY=your-openrouter-api-key
SORTING_HAT_LLM_BASE_URL=https://openrouter.ai/api/v1
SORTING_HAT_LLM_MODEL=anthropic/claude-sonnet-4-20250514
SORTING_HAT_CORS_ORIGINS=["http://localhost:3000"]
SORTING_HAT_DEBUG=true
```

**Step 4: Update `.gitignore`**

Add Python-specific entries:

```
# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
.eggs/
*.egg
.venv/
venv/
```

**Step 5: Run all API tests**

```bash
cd api && pytest tests/ -v
```

Expected: All tests pass.

**Step 6: Commit**

```bash
git add api/ web/ .gitignore
git commit -m "feat: add CORS middleware, environment config, and integration wiring"
```

---

## Task 16: End-to-End Verification

**Step 1: Start Supabase locally (if set up) or verify database connection**

```bash
# If using Supabase CLI:
supabase start
# Apply migration:
supabase db reset
```

Or if connecting to a remote Supabase project, apply migrations through the Supabase dashboard.

**Step 2: Start the API**

```bash
cd api && cp .env.example .env  # Edit with real values
cd api && uvicorn sorting_hat.main:app --reload --port 8000
```

**Step 3: Test health endpoint**

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"ok"}`

**Step 4: Test taxonomy endpoint**

```bash
curl http://localhost:8000/api/v1/taxonomy/governance-groups
```

Expected: Returns list of seeded governance groups.

**Step 5: Start the frontend**

```bash
cd web && cp .env.local.example .env.local
cd web && npm run dev
```

**Step 6: Verify in browser**

Open `http://localhost:3000` — should see sidebar, taxonomy page, classify page.

**Step 7: Commit any fixes**

```bash
git add -A && git commit -m "fix: end-to-end integration fixes"
```

---

## Summary

| Task | What It Builds | Key Files |
|------|---------------|-----------|
| 1 | FastAPI scaffolding + health endpoint | `api/` structure, `main.py`, `pyproject.toml` |
| 2 | Database models (SQLAlchemy) + SQL migration | `models/`, `supabase/migrations/001` |
| 3 | Pydantic request/response schemas | `schemas/` |
| 4 | Taxonomy CRUD service layer | `services/taxonomy.py` |
| 5 | Taxonomy API routes | `routes/taxonomy.py` |
| 6 | LLM provider abstraction | `llm/` |
| 7 | URL scraper service | `services/scraper.py` |
| 8 | Classification pipeline | `services/classifier.py`, `prompts/` |
| 9 | Classification API routes | `routes/classification.py` |
| 10 | Taxonomy seed data | `seed.py`, `migrations/002` |
| 11 | Next.js scaffolding | `web/` structure |
| 12 | shadcn/ui + layout + page shells | sidebar, layout, pages |
| 13 | API client + taxonomy tree + node detail | `api.ts`, tree component |
| 14 | Classification UI | form, result, pipeline view |
| 15 | CORS, env config, integration wiring | middleware, `.env` files |
| 16 | End-to-end verification | manual testing |
