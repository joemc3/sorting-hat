# Deployment Design — The Sorting Hat

**Date:** 2026-02-06
**Status:** Draft

## Overview

Dockerize the Sorting Hat for local development and VPS deployment. Three-layer architecture: Supabase self-hosted (infrastructure), application containers (API + Web), and Traefik reverse proxy (VPS only). CI/CD via GitHub Actions builds images and deploys to the VPS.

## Architecture

### Three Layers

**Layer 1: Supabase (infrastructure)**
- Supabase's official self-hosted docker-compose, trimmed to essential services
- Provides: PostgreSQL (with `ltree`), Auth (GoTrue for future OAuth), Studio dashboard
- Runs on its own Docker network (`supabase_network`)

**Layer 2: Application**
- `docker-compose.yml` in the project root
- Two services: `api` (FastAPI) and `web` (Next.js)
- Connects to `supabase_network` to reach Postgres and Auth
- Has its own network (`app_network`) for inter-service communication
- Locally: publishes ports for direct access (3000, 8000)
- On VPS: no published ports, only reachable via Traefik

**Layer 3: Traefik (VPS only)**
- Separate docker-compose in `deploy/traefik/`
- Binds to host ports 80/443 only
- Connects to `app_network`, routes to `web` service
- Auto-provisions Let's Encrypt SSL for `2524.info`
- The API is never exposed externally — Next.js proxies to it

### Traffic Flow

**On VPS:**
```
Internet → Traefik (:443) → Next.js → FastAPI → PostgreSQL
                                              ↘ Supabase Auth (future)
```

**Locally:**
```
Browser → localhost:3000 (Next.js) → FastAPI (:8000) → PostgreSQL
```

## Docker Images

### API (FastAPI)

Multi-stage Python build:
- Stage 1: Install dependencies from `pyproject.toml` into a virtual env
- Stage 2: Copy the venv + source code into a slim Python 3.12 image
- Runs Alembic migrations on startup, then launches Uvicorn

### Web (Next.js)

Multi-stage Node build:
- Stage 1: `npm ci` to install dependencies
- Stage 2: `npm run build` to produce Next.js standalone output
- Stage 3: Copy the standalone build into a slim Node 22 image
- Standalone mode produces a self-contained server — no `node_modules` at runtime

### Key Decisions

- API handles its own migrations via Alembic at startup (not Supabase CLI)
- Existing SQL files in `supabase/migrations/` get translated into Alembic versions
- Seed data (governance groups + taxonomy nodes) runs as part of the migration chain
- Environment variables passed at runtime via docker-compose, never baked into images
- Next.js proxies API requests server-side — FastAPI is never exposed externally

## Supabase Self-Hosted

### Services We Use

- `db` — PostgreSQL 15 with extensions (including `ltree`)
- `auth` — GoTrue (Supabase Auth) for future OAuth
- `studio` — Supabase dashboard UI (useful for debugging, optional in production)
- `rest` — PostgREST (Auth depends on it)
- `meta` — Metadata service (Studio depends on it)

### Services Disabled

- Realtime, Storage, Edge Functions, imgproxy, Analytics, Logflare, Vector

### Configuration

- Supabase `.env` controls ports, JWT secrets, Postgres credentials
- API's `DATABASE_URL` points at Supabase's Postgres container
- Supabase network created as external so app compose can join it
- Studio accessible locally for database inspection
- On VPS, Studio stays unexposed unless explicitly routed

### Migration Path to Supabase Cloud

When moving to production:
- Swap `DATABASE_URL` to Supabase Cloud's connection string
- Alembic migrations run the same way
- Auth config changes from self-hosted GoTrue to Supabase Cloud Auth
- The `deploy/supabase/` compose stops being used

## CI/CD Pipeline

### GitHub Actions (`.github/workflows/deploy.yml`)

**On push to `main`:**
1. **Lint & Test** — `ruff` + `pytest` for API, `eslint` + `npm run build` for web
2. **Build images** — Multi-stage Docker builds for `api` and `web`
3. **Push to ghcr.io** — Tagged with `latest` and git SHA
4. **Deploy** — SSH into VPS, pull new images, `docker compose up -d`

### GitHub Secrets Required

- `VPS_HOST` — IP or hostname of the VPS
- `VPS_SSH_KEY` — Private key for SSH access
- `VPS_USER` — SSH user

### Deployment Command on VPS

```bash
docker compose pull
docker compose up -d
```

Alembic migrations run automatically on API container startup.

### Intentionally Excluded

- No staging environment
- No rollback automation (redeploy previous SHA manually)
- No branch preview deploys

## Deliverables

### Files to Create

```
sorting-hat/
├── api/
│   ├── Dockerfile
│   ├── alembic/versions/
│   │   ├── 001_initial_schema.py
│   │   └── 002_seed_governance_groups.py
│   └── entrypoint.sh
├── web/
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
├── .env.example
├── deploy/
│   ├── supabase/
│   │   ├── docker-compose.yml
│   │   └── .env.example
│   └── traefik/
│       ├── docker-compose.yml
│       └── traefik.yml
├── .github/
│   └── workflows/
│       └── deploy.yml
└── docs/
    └── vps-setup.md
```

### Files to Update

- `README.md` — Add setup instructions, link to VPS guide, development workflow
- `web/` — Add Next.js API proxy routes
- `api/alembic/` — Convert Supabase SQL migrations to Alembic versions

### VPS Setup Guide (`docs/vps-setup.md`)

Step-by-step covering:
- Installing Docker + Docker Compose on Ubuntu
- Creating a deploy user with SSH key auth
- Cloning the repo, setting up `.env` files
- Starting Supabase, then the app, then Traefik
- Verifying SSL and the full stack
- Firewall config (UFW with Docker awareness)

### Not Creating

- No Kubernetes manifests
- No Terraform/infrastructure-as-code
- No monitoring stack (Prometheus, Grafana, etc.)

## Local Development vs VPS

| Concern | Local | VPS |
|---------|-------|-----|
| Proxy | None — direct port access | Traefik with SSL |
| Ports exposed | 3000 (web), 8000 (api), 54323 (studio) | 80, 443 only (Traefik) |
| SSL | None | Auto via Let's Encrypt |
| Domain | localhost | 2524.info |
| Supabase Studio | Accessible | Unexposed by default |
| UFW concern | N/A (macOS) | Docker bypasses UFW — Traefik solves this |
