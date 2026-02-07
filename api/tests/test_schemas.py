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
