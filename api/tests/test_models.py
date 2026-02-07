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
