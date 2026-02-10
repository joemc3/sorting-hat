import json

from sorting_hat.services.classifier import ClassifierService
from sorting_hat.prompts import SUMMARIZE_SYSTEM, CLASSIFY_SYSTEM
from sorting_hat.prompts.summarize import SUMMARIZE_USER
from sorting_hat.prompts.classify import CLASSIFY_USER


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
