import pytest
from unittest.mock import AsyncMock, MagicMock

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


@pytest.mark.asyncio
async def test_search_nodes_includes_ancestors():
    """search_nodes should include ancestor nodes so the tree renders correctly."""
    grandparent = MagicMock()
    grandparent.id = "gp-id"
    grandparent.parent_id = None
    grandparent.name = "Software"
    grandparent.path = "software"

    parent = MagicMock()
    parent.id = "p-id"
    parent.parent_id = "gp-id"
    parent.name = "App Dev"
    parent.path = "software.app_dev"

    child = MagicMock()
    child.id = "c-id"
    child.parent_id = "p-id"
    child.name = "IDEs & Code Editors"
    child.path = "software.app_dev.ides"

    session = AsyncMock()
    # First call: search query returns only the child
    search_result = MagicMock()
    search_result.scalars.return_value.all.return_value = [child]
    # Second call: fetch parent
    parent_result = MagicMock()
    parent_result.scalars.return_value.all.return_value = [parent]
    # Third call: fetch grandparent
    grandparent_result = MagicMock()
    grandparent_result.scalars.return_value.all.return_value = [grandparent]

    session.execute.side_effect = [search_result, parent_result, grandparent_result]

    service = TaxonomyService(session)
    results = await service.search_nodes("IDE")

    ids = [n.id for n in results]
    assert "c-id" in ids, "Matching child node should be in results"
    assert "p-id" in ids, "Parent ancestor should be in results"
    assert "gp-id" in ids, "Grandparent ancestor should be in results"
