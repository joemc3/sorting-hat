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
