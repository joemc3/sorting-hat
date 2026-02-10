"""Initial schema

Revision ID: 001a
Revises:
Create Date: 2026-02-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "001a"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS ltree")

    op.execute("DO $$ BEGIN CREATE TYPE branch AS ENUM ('software', 'hardware'); EXCEPTION WHEN duplicate_object THEN NULL; END $$")
    op.execute("DO $$ BEGIN CREATE TYPE step_type AS ENUM ('scrape', 'summarize', 'classify'); EXCEPTION WHEN duplicate_object THEN NULL; END $$")

    op.create_table(
        "governance_groups",
        sa.Column("id", UUID(as_uuid=False), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("covers_software", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("covers_hardware", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "taxonomy_nodes",
        sa.Column("id", UUID(as_uuid=False), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("governance_group_id", UUID(as_uuid=False), sa.ForeignKey("governance_groups.id"), nullable=False),
        sa.Column("parent_id", UUID(as_uuid=False), sa.ForeignKey("taxonomy_nodes.id"), nullable=True),
        sa.Column("path", sa.String(1000), nullable=False),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("slug", sa.String(300), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("branch", sa.String(20), nullable=False),
        sa.Column("definition", sa.Text(), nullable=False, server_default=""),
        sa.Column("distinguishing_characteristics", sa.Text(), nullable=False, server_default=""),
        sa.Column("inclusions", sa.Text(), nullable=False, server_default=""),
        sa.Column("exclusions", sa.Text(), nullable=False, server_default=""),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("parent_id", "slug", name="uq_node_parent_slug"),
    )

    # Convert path column to ltree type
    op.execute("ALTER TABLE taxonomy_nodes ALTER COLUMN path TYPE ltree USING path::ltree")

    op.create_index("idx_taxonomy_nodes_path", "taxonomy_nodes", ["path"], postgresql_using="gist")
    op.create_index("idx_taxonomy_nodes_governance_group", "taxonomy_nodes", ["governance_group_id"])
    op.create_index("idx_taxonomy_nodes_parent", "taxonomy_nodes", ["parent_id"])
    op.create_index("idx_taxonomy_nodes_branch", "taxonomy_nodes", ["branch"])

    op.create_table(
        "classifications",
        sa.Column("id", UUID(as_uuid=False), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("url", sa.String(2000), nullable=False),
        sa.Column("raw_content", sa.Text(), nullable=False, server_default=""),
        sa.Column("product_summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("primary_node_id", UUID(as_uuid=False), sa.ForeignKey("taxonomy_nodes.id"), nullable=True),
        sa.Column("secondary_node_ids", sa.ARRAY(UUID(as_uuid=False)), nullable=False, server_default="{}"),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("model_used", sa.String(200), nullable=False, server_default=""),
        sa.Column("model_params", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("reasoning", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("idx_classifications_url", "classifications", ["url"])
    op.create_index("idx_classifications_primary_node", "classifications", ["primary_node_id"])

    op.create_table(
        "classification_steps",
        sa.Column("id", UUID(as_uuid=False), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("classification_id", UUID(as_uuid=False), sa.ForeignKey("classifications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("step_type", sa.String(20), nullable=False),
        sa.Column("input_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("output_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("model_used", sa.String(200), nullable=False, server_default=""),
        sa.Column("tokens_used", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("latency_ms", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("idx_classification_steps_classification", "classification_steps", ["classification_id"])

    # Cast placeholder columns to their enum types
    op.execute("ALTER TABLE taxonomy_nodes ALTER COLUMN branch TYPE branch USING branch::branch")
    op.execute("ALTER TABLE classification_steps ALTER COLUMN step_type TYPE step_type USING step_type::step_type")

    # Auto-update updated_at trigger
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """)

    op.execute("""
        CREATE TRIGGER trg_governance_groups_updated_at
            BEFORE UPDATE ON governance_groups
            FOR EACH ROW EXECUTE FUNCTION update_updated_at()
    """)

    op.execute("""
        CREATE TRIGGER trg_taxonomy_nodes_updated_at
            BEFORE UPDATE ON taxonomy_nodes
            FOR EACH ROW EXECUTE FUNCTION update_updated_at()
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_taxonomy_nodes_updated_at ON taxonomy_nodes")
    op.execute("DROP TRIGGER IF EXISTS trg_governance_groups_updated_at ON governance_groups")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at()")

    op.drop_table("classification_steps")
    op.drop_table("classifications")
    op.drop_table("taxonomy_nodes")
    op.drop_table("governance_groups")

    sa.Enum(name="step_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="branch").drop(op.get_bind(), checkfirst=True)

    op.execute("DROP EXTENSION IF EXISTS ltree")
