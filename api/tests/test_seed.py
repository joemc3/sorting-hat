from sorting_hat.seed import make_id, slugify, escape_sql, GOVERNANCE_GROUPS, generate_governance_groups_sql


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
