"""Parse taxonomy research docs and generate seed SQL for the initial taxonomy data.

Usage: python -m sorting_hat.seed > supabase/migrations/002_seed_taxonomy.sql
"""

import re
from uuid import uuid5, NAMESPACE_DNS


# Deterministic UUIDs so seeds are idempotent
def make_id(name: str) -> str:
    return str(uuid5(NAMESPACE_DNS, f"sorting-hat.{name}"))


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def escape_sql(text: str) -> str:
    return text.replace("'", "''")


GROUP_NUMBER_TO_SLUG: dict[int, str] = {
    1: "application-development-platform",
    2: "business-operations",
    3: "customer-revenue-technology",
    4: "data-analytics",
    5: "collaboration-communication",
    6: "end-user-computing",
    7: "security",
    8: "it-operations-infrastructure",
    9: "engineering-design",
    10: "networking",
}

DUAL_BRANCH_GROUPS: set[str] = {
    "collaboration-communication",
    "end-user-computing",
    "security",
    "it-operations-infrastructure",
    "networking",
}

GOVERNANCE_GROUPS = [
    {
        "name": "Application Development & Platform",
        "slug": "application-development-platform",
        "description": "Building, testing, deploying, and maintaining software; developer tools and platforms",
        "covers_software": True,
        "covers_hardware": False,
        "sort_order": 1,
    },
    {
        "name": "Business Operations",
        "slug": "business-operations",
        "description": "Back-office systems: ERP, finance, HR, procurement, supply chain, legal, compliance",
        "covers_software": True,
        "covers_hardware": False,
        "sort_order": 2,
    },
    {
        "name": "Customer & Revenue Technology",
        "slug": "customer-revenue-technology",
        "description": "Front-office systems: CRM, marketing, sales enablement, e-commerce, customer success",
        "covers_software": True,
        "covers_hardware": False,
        "sort_order": 3,
    },
    {
        "name": "Data & Analytics",
        "slug": "data-analytics",
        "description": "Collecting, storing, processing, analyzing, and visualizing data; AI/ML platforms",
        "covers_software": True,
        "covers_hardware": False,
        "sort_order": 4,
    },
    {
        "name": "Collaboration & Communication",
        "slug": "collaboration-communication",
        "description": "Enabling people to work together and communicate, both software and physical devices",
        "covers_software": True,
        "covers_hardware": True,
        "sort_order": 5,
    },
    {
        "name": "End-User Computing",
        "slug": "end-user-computing",
        "description": "Individual productivity software and personal work devices",
        "covers_software": True,
        "covers_hardware": True,
        "sort_order": 6,
    },
    {
        "name": "Security",
        "slug": "security",
        "description": "Protecting information, systems, and infrastructure from threats",
        "covers_software": True,
        "covers_hardware": True,
        "sort_order": 7,
    },
    {
        "name": "IT Operations & Infrastructure",
        "slug": "it-operations-infrastructure",
        "description": "Managing, monitoring, and maintaining IT systems; compute and storage hardware",
        "covers_software": True,
        "covers_hardware": True,
        "sort_order": 8,
    },
    {
        "name": "Engineering & Design",
        "slug": "engineering-design",
        "description": "Specialized tools for engineering, manufacturing, design, and media production",
        "covers_software": True,
        "covers_hardware": False,
        "sort_order": 9,
    },
    {
        "name": "Networking",
        "slug": "networking",
        "description": "Connecting systems, managing network infrastructure, enabling device communication",
        "covers_software": True,
        "covers_hardware": True,
        "sort_order": 10,
    },
]


def parse_definition_fields(text: str) -> dict[str, str]:
    """Extract definition, distinguishing_characteristics, inclusions, exclusions from text."""
    result = {
        "definition": "",
        "distinguishing_characteristics": "",
        "inclusions": "",
        "exclusions": "",
    }

    # Split on known field markers
    markers = [
        ("distinguishing_characteristics", r"\*Distinguishing characteristics:\*"),
        ("inclusions", r"\*Includes:\*"),
        ("exclusions", r"\*Does not include:\*"),
    ]

    remaining = text.strip()

    # Find positions of all markers
    splits: list[tuple[int, str, int]] = []
    for field, pattern in markers:
        m = re.search(pattern, remaining)
        if m:
            splits.append((m.start(), field, m.end()))

    if not splits:
        result["definition"] = remaining
        return result

    # Sort by position
    splits.sort(key=lambda x: x[0])

    # Everything before first marker is the definition
    result["definition"] = remaining[: splits[0][0]].strip()

    # Extract each field
    for i, (_, field, end) in enumerate(splits):
        if i + 1 < len(splits):
            value = remaining[end : splits[i + 1][0]].strip()
        else:
            value = remaining[end:].strip()
        result[field] = value

    return result


def generate_governance_groups_sql() -> list[str]:
    statements = []
    for g in GOVERNANCE_GROUPS:
        gid = make_id(g["slug"])
        statements.append(
            f"INSERT INTO governance_groups (id, name, slug, description, covers_software, covers_hardware, sort_order) "
            f"VALUES ('{gid}', '{escape_sql(g['name'])}', '{g['slug']}', "
            f"'{escape_sql(g['description'])}', {str(g['covers_software']).upper()}, "
            f"{str(g['covers_hardware']).upper()}, {g['sort_order']});"
        )
    return statements


def main():
    print("-- Sorting Hat: Taxonomy Seed Data")
    print("-- Generated by sorting_hat.seed")
    print()
    print("-- Governance Groups")
    for stmt in generate_governance_groups_sql():
        print(stmt)
    print()
    print("-- NOTE: Full taxonomy node seeding is handled by the seed management command.")
    print("-- Run: python -m sorting_hat.seed_nodes to populate all ~220 taxonomy nodes.")


if __name__ == "__main__":
    main()
