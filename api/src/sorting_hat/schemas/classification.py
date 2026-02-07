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
