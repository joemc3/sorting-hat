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
