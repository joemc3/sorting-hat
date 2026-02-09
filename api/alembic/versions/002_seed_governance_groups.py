"""Seed governance groups

Revision ID: 002a
Revises: 001a
Create Date: 2026-02-09

"""
from typing import Sequence, Union

from alembic import op

revision: str = "002a"
down_revision: Union[str, None] = "001a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "INSERT INTO governance_groups (id, name, slug, description, covers_software, covers_hardware, sort_order) VALUES "
        "('a6ccbec9-d260-5514-bcf1-a338d862031e', 'Application Development & Platform', 'application-development-platform', "
        "'Building, testing, deploying, and maintaining software; developer tools and platforms', TRUE, FALSE, 1)"
    )
    op.execute(
        "INSERT INTO governance_groups (id, name, slug, description, covers_software, covers_hardware, sort_order) VALUES "
        "('a2369b8b-7b7a-5960-a818-97666056c84c', 'Business Operations', 'business-operations', "
        "'Back-office systems: ERP, finance, HR, procurement, supply chain, legal, compliance', TRUE, FALSE, 2)"
    )
    op.execute(
        "INSERT INTO governance_groups (id, name, slug, description, covers_software, covers_hardware, sort_order) VALUES "
        "('97e0bb13-934a-57ec-9974-85a7b1096c69', 'Customer & Revenue Technology', 'customer-revenue-technology', "
        "'Front-office systems: CRM, marketing, sales enablement, e-commerce, customer success', TRUE, FALSE, 3)"
    )
    op.execute(
        "INSERT INTO governance_groups (id, name, slug, description, covers_software, covers_hardware, sort_order) VALUES "
        "('ad5ae6e1-6a56-58fc-8660-a4799d3132fc', 'Data & Analytics', 'data-analytics', "
        "'Collecting, storing, processing, analyzing, and visualizing data; AI/ML platforms', TRUE, FALSE, 4)"
    )
    op.execute(
        "INSERT INTO governance_groups (id, name, slug, description, covers_software, covers_hardware, sort_order) VALUES "
        "('0074d7ca-e99b-5ec8-9fef-8d4b27661293', 'Collaboration & Communication', 'collaboration-communication', "
        "'Enabling people to work together and communicate, both software and physical devices', TRUE, TRUE, 5)"
    )
    op.execute(
        "INSERT INTO governance_groups (id, name, slug, description, covers_software, covers_hardware, sort_order) VALUES "
        "('d1e9e410-b99a-57fa-836d-30c226cc2b47', 'End-User Computing', 'end-user-computing', "
        "'Individual productivity software and personal work devices', TRUE, TRUE, 6)"
    )
    op.execute(
        "INSERT INTO governance_groups (id, name, slug, description, covers_software, covers_hardware, sort_order) VALUES "
        "('6b5698b2-9016-59c8-aa1c-fa7f087875a6', 'Security', 'security', "
        "'Protecting information, systems, and infrastructure from threats', TRUE, TRUE, 7)"
    )
    op.execute(
        "INSERT INTO governance_groups (id, name, slug, description, covers_software, covers_hardware, sort_order) VALUES "
        "('5598220c-cef5-5e86-b0ae-b427e4248575', 'IT Operations & Infrastructure', 'it-operations-infrastructure', "
        "'Managing, monitoring, and maintaining IT systems; compute and storage hardware', TRUE, TRUE, 8)"
    )
    op.execute(
        "INSERT INTO governance_groups (id, name, slug, description, covers_software, covers_hardware, sort_order) VALUES "
        "('1e8729f1-74be-585c-9640-6a48a09590c9', 'Engineering & Design', 'engineering-design', "
        "'Specialized tools for engineering, manufacturing, design, and media production', TRUE, FALSE, 9)"
    )
    op.execute(
        "INSERT INTO governance_groups (id, name, slug, description, covers_software, covers_hardware, sort_order) VALUES "
        "('b388ccd7-4249-5c0c-803e-f906d0a40a58', 'Networking', 'networking', "
        "'Connecting systems, managing network infrastructure, enabling device communication', TRUE, TRUE, 10)"
    )


def downgrade() -> None:
    op.execute("DELETE FROM governance_groups")
