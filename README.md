# The Sorting Hat

An open, architectural taxonomy for classifying enterprise software and compute-related hardware by product capability.

## What Is This?

The Sorting Hat is a product for classifying enterprise IT products into a structured taxonomy. It consists of:

1. **A taxonomy** — 278 nodes across 10 governance groups with natural-language definitions at every node
2. **A taxonomy management API** — full CRUD for governance groups and taxonomy nodes, search, subtree queries
3. **A classification API** — accepts a product URL, scrapes the page, and uses an LLM to classify the product into the correct taxonomy node(s)
4. **A single front end** — taxonomy browser with tree visualization and a classification interface for submitting URLs

## How Classification Works

The classification API runs a 3-step AI pipeline:

1. **Scrape** — Fetches the product URL and extracts clean text content from the page
2. **Summarize** — An LLM reads the extracted content and produces a structured product summary: name, primary function, key capabilities, target users, and category signals
3. **Classify** — A second LLM call receives the product summary alongside the full taxonomy (with definitions at every node) and returns a JSON classification: one primary category, up to two secondaries, confidence score, and reasoning

Each step is logged with its input, output, model used, token count, and latency — making the classification pipeline fully auditable.

The LLM provider is pluggable via an OpenAI-compatible abstraction. Supported backends:
- **OpenRouter** (default) — access to Claude, GPT-4, and other models
- **OpenAI** — direct OpenAI API
- **Ollama** — local models for development and testing

## Taxonomy Design Principles

- **Classify by capability, not delivery model** — SaaS vs on-prem is irrelevant; what the product *does* determines placement
- **Hardware and software are always separate branches** — Level 1 splits into Software and Computing Hardware; they never merge
- **Governance groups are the tree** — 10 groups form Level 2 and map directly to organizational standards/governance teams
- **Multi-category classification** — exactly one primary category (governance ownership), up to two secondary categories (cross-functional visibility)
- **Definitions at every node** — written for AI-driven classification; the system matches product webpages against these definitions
- **Flexible depth** — branches go 3-5 levels deep following domain complexity, not arbitrary rules
- **No product catalog** — the taxonomy classifies products but doesn't maintain a list of them
- **No financial layers** — purely architectural, not for cost/spend management

## The 10 Governance Groups

| # | Governance Group | SW | HW | Scope |
|---|-----------------|----|----|-------|
| 1 | Application Development & Platform | Yes | — | Building, testing, deploying, and maintaining software |
| 2 | Business Operations | Yes | — | ERP, finance, HR, procurement, supply chain, legal, compliance |
| 3 | Customer & Revenue Technology | Yes | — | CRM, marketing, sales enablement, e-commerce, customer success |
| 4 | Data & Analytics | Yes | — | Databases, warehouses, ETL, BI, ML/AI, data governance |
| 5 | Collaboration & Communication | Yes | Yes | Messaging, video, project management, wikis, conferencing devices |
| 6 | End-User Computing | Yes | Yes | Office suites, browsers, laptops, desktops, peripherals |
| 7 | Security | Yes | Yes | IAM, endpoint protection, SIEM, DLP, firewalls, HSMs |
| 8 | IT Operations & Infrastructure | Yes | Yes | ITSM, monitoring, backup, virtualization, servers, storage |
| 9 | Engineering & Design | Yes | — | CAD, CAM, CAE, PLM, UX design, media production, GIS |
| 10 | Networking | Yes | Yes | SDN, network monitoring, SD-WAN, switches, routers, wireless |

## Architecture

```
                          ┌→ Next.js (web)
Internet → Traefik (:443) ┤
                          └→ FastAPI (api) → PostgreSQL
                                           → LLM Provider (OpenRouter / OpenAI / Ollama)
```

Traefik routes by path: requests to `/api/` go directly to FastAPI, everything else goes to Next.js.

- **API** — FastAPI (Python 3.12) with SQLAlchemy async, Alembic migrations, pluggable LLM provider
- **Web** — Next.js 16 (App Router, TypeScript, Tailwind CSS, shadcn/ui)
- **Database** — PostgreSQL 15 with `ltree` extension for tree-structured taxonomy paths
- **Proxy** — Traefik with auto-provisioned Let's Encrypt SSL (VPS only)

### API Endpoints

**Taxonomy Management** (`/api/v1/taxonomy`)
- `GET /governance-groups` — List all governance groups
- `POST /governance-groups` — Create a governance group
- `GET/PUT/DELETE /governance-groups/{slug}` — CRUD by slug
- `GET /nodes` — List taxonomy nodes (filter by branch, governance group, depth)
- `GET /nodes/search?q=` — Full-text search across node names and definitions
- `GET /nodes/{id}` — Node detail with children and parent chain
- `GET /nodes/{id}/subtree` — Full subtree under a node
- `POST/PUT/DELETE /nodes` — CRUD for taxonomy nodes

**Classification** (`/api/v1/classify`)
- `POST /classify` — Submit a URL for AI classification (returns primary + secondary nodes, confidence, reasoning)
- `GET /classify/{id}` — Full classification detail including all pipeline steps
- `GET /classify` — List past classifications (filter by URL)

## Quick Start (Docker)

```bash
# Clone and configure
git clone https://github.com/joemc3/sorting-hat.git
cd sorting-hat
cp .env.example .env
# Edit .env — set POSTGRES_PASSWORD and SORTING_HAT_LLM_API_KEY

# Start everything
docker compose up -d

# Access
# Web:    http://localhost:3000
# API:    http://localhost:8000
# Health: http://localhost:8000/api/health
```

## Local Development (without Docker)

```bash
# API
cd api
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # Edit with your database URL and LLM API key
uvicorn sorting_hat.main:app --reload

# Web (separate terminal)
cd web
npm install
npm run dev
```

Requires a PostgreSQL instance with the `ltree` extension — see `api/.env.example` for connection config.

## Running Tests

```bash
# API tests
cd api && source .venv/bin/activate
pytest tests/ -q
ruff check .

# Web lint
cd web
npm run lint
```

## Deployment

See [docs/vps-setup.md](docs/vps-setup.md) for full VPS deployment instructions.

CI/CD via GitHub Actions: push to `main` runs linting and tests, builds Docker images, and pushes to ghcr.io. Deployment to the VPS is manual — pull the updated images and restart services.

## Codebase Statistics

| Area | Files | Lines of Code |
|------|------:|-------------:|
| Python source (`api/src/`) | 24 | 1,656 |
| Python tests (`api/tests/`) | 10 | 529 |
| TypeScript/TSX (`web/src/`) | 19 | 1,163 |
| **Total** | **53** | **3,348** |

| Metric | Count |
|--------|------:|
| API endpoints | 16 (12 taxonomy, 3 classification, 1 health) |
| Database models | 4 (GovernanceGroup, TaxonomyNode, Classification, ClassificationStep) |
| Alembic migrations | 3 |
| Seeded taxonomy nodes | 278 across 10 governance groups |
| Test files | 10 (all Python; no frontend tests yet) |
| Test cases | 55 |
| Python dependencies | 16 (11 runtime + 5 dev) |
| JavaScript dependencies | 18 (8 runtime + 10 dev) |
| Docker services | 3 (api, web, db) |

## License

TBD
