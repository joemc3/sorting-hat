import re

from sorting_hat.seed import (
    make_id,
    slugify,
    escape_sql,
    GOVERNANCE_GROUPS,
    generate_governance_groups_sql,
    GROUP_NUMBER_TO_SLUG,
    DUAL_BRANCH_GROUPS,
    parse_definition_fields,
    parse_taxonomy_definitions,
    generate_taxonomy_nodes_sql,
)

import os

RESEARCH_DOC = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "research", "Taxonomy Definitions - Complete Reference.md",
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


# --- parse_taxonomy_definitions tests ---


def test_parse_taxonomy_definitions_total_count():
    nodes = parse_taxonomy_definitions(RESEARCH_DOC)
    assert len(nodes) >= 220


def test_parse_taxonomy_definitions_level_2_count():
    nodes = parse_taxonomy_definitions(RESEARCH_DOC)
    l2 = [n for n in nodes if n["level"] == 2]
    assert len(l2) == 15  # 5 SW-only + 5 dual * 2


def test_parse_taxonomy_definitions_branches():
    nodes = parse_taxonomy_definitions(RESEARCH_DOC)
    for n in nodes:
        assert n["branch"] in ("software", "hardware")


def test_parse_taxonomy_definitions_paths_unique():
    nodes = parse_taxonomy_definitions(RESEARCH_DOC)
    paths = [n["path"] for n in nodes]
    assert len(paths) == len(set(paths))


def test_parse_taxonomy_definitions_parent_paths_valid():
    nodes = parse_taxonomy_definitions(RESEARCH_DOC)
    all_paths = {n["path"] for n in nodes}
    for n in nodes:
        if n["level"] > 2:
            assert n["parent_path"] in all_paths, (
                f"Node {n['path']} has parent_path {n['parent_path']} not in all_paths"
            )


def test_parse_taxonomy_definitions_dual_branch_groups():
    nodes = parse_taxonomy_definitions(RESEARCH_DOC)
    dual_slugs = {
        "collaboration-communication",
        "end-user-computing",
        "security",
        "it-operations-infrastructure",
        "networking",
    }
    for slug in dual_slugs:
        branches = {n["branch"] for n in nodes if n["governance_group_slug"] == slug}
        assert branches == {"software", "hardware"}, (
            f"Group {slug} has branches {branches}, expected both"
        )


def test_parse_taxonomy_definitions_ltree_valid_paths():
    nodes = parse_taxonomy_definitions(RESEARCH_DOC)
    for n in nodes:
        for label in n["path"].split("."):
            assert re.match(r"^[a-zA-Z0-9_]+$", label), (
                f"Invalid ltree label '{label}' in path '{n['path']}'"
            )


def test_parse_taxonomy_definitions_has_definitions():
    nodes = parse_taxonomy_definitions(RESEARCH_DOC)
    for n in nodes:
        assert n["definition"], f"Node {n['path']} has empty definition"


# --- generate_taxonomy_nodes_sql tests ---


def test_generate_taxonomy_nodes_sql_count():
    stmts = generate_taxonomy_nodes_sql()
    assert len(stmts) >= 220


def test_generate_taxonomy_nodes_sql_all_insert():
    stmts = generate_taxonomy_nodes_sql()
    assert all("INSERT INTO taxonomy_nodes" in s for s in stmts)


def test_generate_taxonomy_nodes_sql_level_ordering():
    """Level 2 before 3 before 4 (FK constraint requires parents first)."""
    stmts = generate_taxonomy_nodes_sql()
    levels = []
    for s in stmts:
        # Extract level from SQL
        m = re.search(r",\s*(\d+),\s*'(software|hardware)'", s)
        if m:
            levels.append(int(m.group(1)))
    # Levels should be non-decreasing
    for i in range(1, len(levels)):
        assert levels[i] >= levels[i - 1], (
            f"Level ordering violated at index {i}: {levels[i - 1]} > {levels[i]}"
        )


def test_generate_taxonomy_nodes_sql_deterministic():
    assert generate_taxonomy_nodes_sql() == generate_taxonomy_nodes_sql()


def test_generate_taxonomy_nodes_sql_no_unescaped_quotes():
    stmts = generate_taxonomy_nodes_sql()
    for s in stmts:
        # After removing escaped quotes (''), there should be an even number of '
        cleaned = s.replace("''", "")
        count = cleaned.count("'")
        assert count % 2 == 0, f"Unbalanced quotes in: {s[:100]}..."
