# The Sorting Hat — System Design

> Validated design for the full Sorting Hat product: taxonomy management API, classification API, and front end.

---

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend | Python + FastAPI | Best AI/LLM ecosystem; strong API framework |
| Front end | Next.js App Router + Tailwind + shadcn/ui | Modern React, great DX, clean components |
| Database | PostgreSQL via Supabase | Postgres features (ltree, recursive CTEs) + auth for free |
| Supabase role | Database + auth only | FastAPI owns all business logic; keeps system portable |
| LLM provider | Provider-agnostic | OpenRouter primary, support direct APIs and Ollama |
| Classification flow | Scrape → Summarize → Classify | Separates understanding from classification; debuggable |
| Repo structure | Monorepo, deploy separately | Single repo, independent deploys for API and web |

---

## High-Level Architecture

```
sorting-hat/
├── api/          # Python FastAPI — taxonomy management + classification
├── web/          # Next.js App Router — single UI for both workflows
├── research/     # Taxonomy research docs (already exists)
├── supabase/     # Migrations, seed data, schema
└── docs/         # Design docs, plans
```

**Three runtime components:**

- **FastAPI service** (`api/`) — Exposes two groups of endpoints: taxonomy CRUD (manage nodes, definitions, governance groups, tree structure) and classification (accept URL, scrape, summarize, classify). All business logic lives here.
- **Next.js app** (`web/`) — Single front end serving two workflows: a taxonomy browser/editor for managing the tree, and a classification interface for submitting URLs and viewing results. Talks only to the FastAPI service.
- **Supabase** — PostgreSQL database (taxonomy schema, classification history), auth (Supabase Auth for user management), and nothing else. No PostgREST, no Edge Functions. Just the database and auth services.

**Key constraint:** The FastAPI service is the only thing that talks to the database. The front end never hits Supabase directly (except for auth token management). This keeps the API as the single source of truth and makes Supabase swappable.

**The classification flow:**
`URL → Scrape & extract → LLM summarizes product → LLM classifies summary against taxonomy → Return primary + secondaries`

---

## Data Model

The taxonomy is a tree stored in PostgreSQL using the **adjacency list + materialized path** pattern. Adjacency list (parent_id) keeps writes simple; materialized path (ltree) makes tree queries fast.

### Core tables

```sql
governance_groups
  id, name, slug, description, covers_software, covers_hardware, sort_order

taxonomy_nodes
  id, governance_group_id, parent_id, path (ltree),
  name, slug, level, branch (enum: 'software' | 'hardware'),
  definition, distinguishing_characteristics,
  inclusions, exclusions,
  sort_order, created_at, updated_at

classifications
  id, url, raw_content, product_summary,
  primary_node_id (FK → taxonomy_nodes),
  secondary_node_ids (array, max 2),
  confidence_score, model_used, model_params,
  created_at

classification_steps
  id, classification_id, step_type (enum: 'scrape' | 'summarize' | 'classify'),
  input_text, output_text, model_used,
  tokens_used, latency_ms, created_at
```

### Design rationale

- **governance_groups** as a separate table (not just level-2 nodes) because they carry metadata the tree doesn't — which branches they cover (SW/HW/both), mapping to organizational teams.
- **taxonomy_nodes.definition** is split into four fields matching the research doc format: definition, distinguishing characteristics, inclusions, exclusions. This gives the classification LLM structured input rather than one blob.
- **classification_steps** logs every stage of the pipeline (scrape, summarize, classify) separately. This is how you debug misclassifications — you can see exactly what the LLM received and returned at each step.
- **ltree path** enables queries like "give me everything under IT Operations" without recursive CTEs.

---

## Taxonomy Management API

All routes under `/api/v1/taxonomy`.

### Governance Groups

- `GET /governance-groups` — List all 10 groups with metadata
- `GET /governance-groups/:slug` — Single group with its top-level nodes
- `POST/PUT/DELETE /governance-groups` — Manage groups

### Taxonomy Nodes

- `GET /nodes` — Full tree (with query params for filtering by branch, governance group, depth)
- `GET /nodes/:id` — Single node with parent chain and children
- `GET /nodes/:id/subtree` — Full subtree rooted at a node
- `POST /nodes` — Create node (parent_id required, ltree path auto-computed)
- `PUT /nodes/:id` — Update node (name, definition fields, sort order)
- `DELETE /nodes/:id` — Delete node (fails if it has children — must delete leaves first)
- `POST /nodes/:id/move` — Re-parent a node (recalculates ltree paths for entire subtree)

### Search & Lookup

- `GET /nodes/search?q=...` — Full-text search across names and definitions
- `GET /nodes/by-path/:ltree_path` — Lookup by materialized path

### Tree integrity rules (enforced at the API layer)

- A node's branch (software/hardware) must match its parent's branch
- Level is auto-calculated from depth, not manually set
- Governance group is inherited from the level-2 ancestor, not set per-node
- Moving a node across branches or governance groups is rejected

### Seeding

The existing taxonomy from the research docs becomes a seed migration. The ~220 nodes, all definitions, and all governance groups get loaded into Supabase as the initial dataset.

---

## Classification API

Lives alongside the taxonomy API in the same FastAPI service, under `/api/v1/classify`.

### Endpoints

- `POST /classify` — Accept a URL, run the full pipeline, return results
- `GET /classify/:id` — Retrieve a past classification with full step history
- `GET /classify/history` — List past classifications (paginated, filterable by URL, node, date)

### The three-step pipeline

**Step 1: Scrape.** Fetch the URL, extract meaningful content. Strip navigation, ads, footers, cookie banners. Pull out the product name, description, feature lists, and any "what it does" language. Store the raw HTML and extracted text. This is plain Python — no LLM needed. Libraries like `httpx` + `beautifulsoup4` or `trafilatura` (purpose-built for content extraction) handle this.

**Step 2: Summarize.** Send the extracted content to the LLM with a focused prompt: "What does this product do? What capabilities does it provide? Who uses it?" The output is a structured product summary — not a classification yet. This summary is stored and becomes the input to step 3.

**Step 3: Classify.** Send the product summary + the full taxonomy definitions to the LLM. The prompt asks it to select exactly one primary node (governance ownership) and up to two secondary nodes (cross-functional visibility), with reasoning for each choice. The response is parsed into structured output with node IDs and confidence scores.

### LLM abstraction layer

A `Provider` interface with `complete(messages, model, params)`. Implementations for OpenAI-compatible (covers OpenRouter, Ollama, OpenAI direct) and Anthropic direct. Provider and model are configurable per-request or via environment defaults.

---

## Front End

The Next.js app serves two workflows in a single interface.

### Taxonomy Browser/Editor

- Interactive tree view showing the full taxonomy. Expandable/collapsible nodes, grouped by governance group. Software and Hardware as top-level tabs or a branch toggle.
- Click any node to see its full detail panel: name, definition, distinguishing characteristics, inclusions/exclusions, parent chain (breadcrumb), and direct children.
- Edit in place — click to edit any field on a node. Add child nodes, reorder, delete leaves.
- Search bar that filters the tree in real time by name or definition content.

### Classification Interface

- A simple input: paste a URL, hit classify.
- Results display: product summary (what the LLM understood), primary classification shown as a breadcrumb path through the tree (e.g., "Software > Security > Endpoint Security"), secondary classifications if any, confidence score, and the LLM's reasoning.
- Pipeline transparency: expandable section showing each step — what was scraped, what the summary was, what the classifier received. This is the debug view.
- Classification history: searchable list of past classifications.

### Layout

Sidebar navigation with two sections (Taxonomy, Classify). No auth walls for now — Supabase Auth is wired up but we start without login requirements. That gets layered on when needed.

### Component approach

shadcn/ui primitives, Tailwind for layout. The tree component is the most custom piece — built with Radix primitives or a headless tree library rather than fighting a prebuilt component.
