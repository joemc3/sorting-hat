-- Enable ltree extension (Supabase has it available)
CREATE EXTENSION IF NOT EXISTS ltree;

-- Branch enum
CREATE TYPE branch AS ENUM ('software', 'hardware');
CREATE TYPE step_type AS ENUM ('scrape', 'summarize', 'classify');

-- Governance groups
CREATE TABLE governance_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    covers_software BOOLEAN NOT NULL DEFAULT TRUE,
    covers_hardware BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Taxonomy nodes
CREATE TABLE taxonomy_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    governance_group_id UUID NOT NULL REFERENCES governance_groups(id),
    parent_id UUID REFERENCES taxonomy_nodes(id),
    path ltree NOT NULL DEFAULT '',
    name VARCHAR(300) NOT NULL,
    slug VARCHAR(300) NOT NULL,
    level INTEGER NOT NULL,
    branch branch NOT NULL,
    definition TEXT NOT NULL DEFAULT '',
    distinguishing_characteristics TEXT NOT NULL DEFAULT '',
    inclusions TEXT NOT NULL DEFAULT '',
    exclusions TEXT NOT NULL DEFAULT '',
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (parent_id, slug)
);

CREATE INDEX idx_taxonomy_nodes_path ON taxonomy_nodes USING gist (path);
CREATE INDEX idx_taxonomy_nodes_governance_group ON taxonomy_nodes (governance_group_id);
CREATE INDEX idx_taxonomy_nodes_parent ON taxonomy_nodes (parent_id);
CREATE INDEX idx_taxonomy_nodes_branch ON taxonomy_nodes (branch);

-- Classifications
CREATE TABLE classifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url VARCHAR(2000) NOT NULL,
    raw_content TEXT NOT NULL DEFAULT '',
    product_summary TEXT NOT NULL DEFAULT '',
    primary_node_id UUID REFERENCES taxonomy_nodes(id),
    secondary_node_ids UUID[] NOT NULL DEFAULT '{}',
    confidence_score FLOAT,
    model_used VARCHAR(200) NOT NULL DEFAULT '',
    model_params TEXT NOT NULL DEFAULT '{}',
    reasoning TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_classifications_url ON classifications (url);
CREATE INDEX idx_classifications_primary_node ON classifications (primary_node_id);

-- Classification steps
CREATE TABLE classification_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    classification_id UUID NOT NULL REFERENCES classifications(id) ON DELETE CASCADE,
    step_type step_type NOT NULL,
    input_text TEXT NOT NULL DEFAULT '',
    output_text TEXT NOT NULL DEFAULT '',
    model_used VARCHAR(200) NOT NULL DEFAULT '',
    tokens_used INTEGER NOT NULL DEFAULT 0,
    latency_ms INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_classification_steps_classification ON classification_steps (classification_id);

-- Auto-update updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_governance_groups_updated_at
    BEFORE UPDATE ON governance_groups
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_taxonomy_nodes_updated_at
    BEFORE UPDATE ON taxonomy_nodes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
