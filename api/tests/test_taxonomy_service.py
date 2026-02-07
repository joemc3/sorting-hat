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
