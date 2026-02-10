from datetime import datetime

from pydantic import BaseModel, Field


class ClassifyRequest(BaseModel):
    """Submit a product URL for AI-powered classification."""

    url: str = Field(..., max_length=2000, description="Public URL of the product webpage to classify")
    model: str | None = Field(None, description="LLM model to use (defaults to server-configured model)")
    provider: str | None = Field(None, description="LLM provider override")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "url": "https://www.datadoghq.com/",
                    "model": None,
                    "provider": None,
                }
            ]
        }
    }


class ClassificationStepResponse(BaseModel):
    """A single step in the classification pipeline (e.g. page fetch, summarization, classification)."""

    id: str = Field(..., description="Unique identifier (UUID)")
    step_type: str = Field(..., description="Type of step: 'fetch', 'summarize', or 'classify'")
    input_text: str = Field(..., description="Input provided to this step")
    output_text: str = Field(..., description="Output produced by this step")
    model_used: str = Field(..., description="LLM model used for this step")
    tokens_used: int = Field(..., description="Total tokens consumed by this step")
    latency_ms: int = Field(..., description="Wall-clock time for this step in milliseconds")
    created_at: datetime = Field(..., description="When this step was executed")

    model_config = {"from_attributes": True}


class ClassificationResponse(BaseModel):
    """Result of classifying a product URL into the taxonomy."""

    id: str = Field(..., description="Unique identifier (UUID)")
    url: str = Field(..., description="The product URL that was classified")
    product_summary: str = Field(..., description="AI-generated summary of what the product does")
    primary_node_id: str | None = Field(..., description="UUID of the primary taxonomy node")
    primary_node_path: str | None = Field(None, description="Human-readable path (e.g. 'Software > Security > IAM')")
    secondary_node_ids: list[str] = Field(..., description="UUIDs of up to 2 secondary taxonomy nodes")
    secondary_node_paths: list[str] = Field([], description="Human-readable paths for secondary nodes")
    confidence_score: float | None = Field(..., description="AI confidence in the classification (0.0 to 1.0)")
    model_used: str = Field(..., description="LLM model used for classification")
    reasoning: str = Field(..., description="AI explanation of why this classification was chosen")
    created_at: datetime = Field(..., description="When the classification was performed")

    model_config = {"from_attributes": True}


class ClassificationDetail(ClassificationResponse):
    """Full classification with raw page content and all intermediate AI steps."""

    raw_content: str = Field(..., description="Raw text content fetched from the product URL")
    steps: list[ClassificationStepResponse] = Field([], description="Ordered list of AI pipeline steps")
