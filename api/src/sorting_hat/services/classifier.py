import json
import time
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from sorting_hat.llm.provider import LLMMessage, LLMProvider
from sorting_hat.models.classification import Classification, ClassificationStep, StepType
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
        await self.session.flush()
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
