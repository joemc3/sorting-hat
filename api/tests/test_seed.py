from sorting_hat.seed import (
    make_id,
    slugify,
    escape_sql,
    GOVERNANCE_GROUPS,
    generate_governance_groups_sql,
    GROUP_NUMBER_TO_SLUG,
    DUAL_BRANCH_GROUPS,
    parse_definition_fields,
)


def test_make_id_deterministic():
    id1 = make_id("security")
    id2 = make_id("security")
    assert id1 == id2


def test_make_id_unique_per_name():
    id1 = make_id("security")
    id2 = make_id("networking")
    assert id1 != id2


def test_slugify():
    assert slugify("Application Development & Platform") == "application_development_platform"


def test_escape_sql():
    assert escape_sql("it's") == "it''s"


def test_governance_groups_count():
    assert len(GOVERNANCE_GROUPS) == 10


def test_generate_sql_produces_10_inserts():
    stmts = generate_governance_groups_sql()
    assert len(stmts) == 10
    assert all("INSERT INTO governance_groups" in s for s in stmts)


def test_group_number_to_slug_has_all_10():
    assert len(GROUP_NUMBER_TO_SLUG) == 10
    assert GROUP_NUMBER_TO_SLUG[1] == "application-development-platform"
    assert GROUP_NUMBER_TO_SLUG[10] == "networking"


def test_dual_branch_groups():
    assert len(DUAL_BRANCH_GROUPS) == 5
    assert "collaboration-communication" in DUAL_BRANCH_GROUPS
    assert "end-user-computing" in DUAL_BRANCH_GROUPS
    assert "security" in DUAL_BRANCH_GROUPS
    assert "it-operations-infrastructure" in DUAL_BRANCH_GROUPS
    assert "networking" in DUAL_BRANCH_GROUPS
    # Software-only groups should NOT be in dual-branch
    assert "application-development-platform" not in DUAL_BRANCH_GROUPS


def test_parse_definition_fields_all_present():
    text = (
        "Main def. *Distinguishing characteristics:* DC. "
        "*Includes:* Inc. *Does not include:* Exc."
    )
    result = parse_definition_fields(text)
    assert result["definition"] == "Main def."
    assert result["distinguishing_characteristics"] == "DC."
    assert result["inclusions"] == "Inc."
    assert result["exclusions"] == "Exc."


def test_parse_definition_fields_partial():
    text = "Main def. *Distinguishing characteristics:* DC."
    result = parse_definition_fields(text)
    assert result["definition"] == "Main def."
    assert result["distinguishing_characteristics"] == "DC."
    assert result["inclusions"] == ""
    assert result["exclusions"] == ""


def test_parse_definition_fields_definition_only():
    text = "Just a definition."
    result = parse_definition_fields(text)
    assert result["definition"] == "Just a definition."
    assert result["distinguishing_characteristics"] == ""
    assert result["inclusions"] == ""
    assert result["exclusions"] == ""


def test_parse_definition_fields_real_example():
    text = (
        "Tools and technologies for building, testing, deploying, and maintaining "
        "software applications and platforms. This group encompasses the full development "
        "lifecycle from initial coding through production deployment. "
        "*Distinguishing characteristics:* Focuses on the technical tools developers use "
        "to create software; distinct from the infrastructure those applications run on "
        "(IT Operations) and the business applications themselves. "
        "*Includes:* IDEs, programming languages, frameworks, version control, CI/CD, "
        "testing tools, API management, containerization, and developer collaboration tools. "
        "*Does not include:* Infrastructure management platforms, business applications, "
        "or end-user productivity tools."
    )
    result = parse_definition_fields(text)
    assert result["definition"].startswith("Tools and technologies")
    assert "Focuses on the technical tools" in result["distinguishing_characteristics"]
    assert "IDEs, programming languages" in result["inclusions"]
    assert "Infrastructure management" in result["exclusions"]
