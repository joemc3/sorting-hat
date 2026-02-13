# Multi-Agent Code Review — The Sorting Hat

**Date:** 2026-02-13
**Reviewers:** 6 specialized AI agents (Security, Data Layer, Service Layer, Frontend, Infrastructure, Testing)
**Scope:** Full codebase — API, frontend, infrastructure, and test suite

---

## Executive Summary

Six parallel review agents examined the entire Sorting Hat codebase across security, data integrity, business logic, frontend quality, infrastructure, and test coverage. The review identified **96 findings** across all severity levels.

| Severity | Count | Key Themes |
|----------|-------|------------|
| **Critical** | 11 | SSRF, no auth, no LLM retries, unbounded responses, prompt injection, N+1 explosions, empty test infrastructure, containers running as root |
| **High** | 16 | Exception leaking, LIKE injection, no rate limits, N+1 queries, ORM/DDL mismatches, missing node ID validation, no LLM timeout, no frontend error handling |
| **Medium** | 32 | CORS config, URL validation, model selection abuse, connection pooling, schema validation gaps, accessibility, search debounce, migration sync |
| **Low** | 20+ | Magic constants, config defaults, dead code, missing markers, minor UX issues |

**Bottom line:** The architecture is well-designed and the code is clean, but the application is not production-hardened. The three most urgent categories are: (1) security hardening (SSRF + auth + rate limiting), (2) reliability (LLM retries + timeouts + error handling), and (3) test coverage (near-zero for the most critical paths).

---

## Critical Findings (Fix Before Production)

### SEC-1: Full SSRF — No URL Validation in Scraper
**File:** `api/src/sorting_hat/services/scraper.py:13-28`
**Agents:** Security, Service Layer

The scraper fetches any user-provided URL with `follow_redirects=True` and zero validation. An attacker can target:
- Cloud metadata: `http://169.254.169.254/latest/meta-data/` (AWS IAM credential theft)
- Internal services: `http://localhost:5432/`, `http://10.0.0.1/admin`
- Redirect-based bypass: legitimate URL → 302 → internal target

**Fix:**
- Validate URL scheme is `https` (or `http` with explicit opt-in)
- Resolve hostname → reject private/reserved IPs (RFC 1918, link-local, loopback)
- Re-validate after each redirect
- Consider DNS resolution pinning

---

### SEC-2: No Authentication or Authorization on Any Endpoint
**File:** `api/src/sorting_hat/routes/taxonomy.py:1-171`, `api/src/sorting_hat/routes/classification.py:1-117`
**Agent:** Security

Every endpoint — including destructive operations (DELETE governance groups, DELETE taxonomy nodes) and costly operations (POST classify = scrape + 2x LLM calls) — is completely unauthenticated.

**Fix:**
- Add API key or JWT bearer token authentication
- Role-based authorization: reads can be public, writes/deletes need elevated privileges
- At minimum, protect `/api/v1/classify` (each call costs real money)

---

### SEC-3: No Response Body Size Limit on Scraped Pages
**File:** `api/src/sorting_hat/services/scraper.py:29`
**Agent:** Service Layer

`response.text` reads the entire HTTP response into memory with no cap. A multi-gigabyte URL exhausts server memory.

**Fix:**
- Stream the response with `response.aiter_bytes()` and enforce a max size (e.g., 10 MB)
- Check `Content-Type` is `text/html` before reading
- Check `Content-Length` header first as an early reject

---

### SVC-1: No LLM Retry Logic or Transient Error Handling
**File:** `api/src/sorting_hat/llm/openai_compat.py:17-22`
**Agent:** Service Layer

A single failed LLM API call (429, 5xx, network timeout) crashes the entire classification pipeline, wasting the already-completed scrape and summarize work.

**Fix:**
- Implement retry with exponential backoff for retryable errors (429, 500-504, connection errors)
- Use `tenacity` or manual retry wrapper
- Distinguish `RateLimitError` from `APIConnectionError` for logging

---

### SVC-2: Prompt Injection via Scraped Web Content
**File:** `api/src/sorting_hat/services/classifier.py:65, 93-94`
**Agent:** Service Layer

Scraped web content is injected directly into LLM prompts with no sanitization. An adversarial page could embed "Ignore all previous instructions..." to manipulate classification results.

**Fix:**
- Use XML-style delimiters (`<product_content>...</product_content>`) instead of `---`
- Add content sanitization layer
- Post-process: validate returned `node_id` actually exists in taxonomy before persisting

---

### SVC-3: Classification Silently Succeeds with Null Primary Node
**File:** `api/src/sorting_hat/services/classifier.py:114-123`
**Agent:** Service Layer

When `_parse_classification` fails to parse LLM JSON, `primary_node_id` becomes `None`, but the classification is still committed as a "successful" record. No signal to callers that it failed.

**Fix:**
- Raise `ClassificationError` when `primary_node_id` is `None`
- Or add a `status` field to `Classification` (`"completed"` / `"failed"`)
- Retry the LLM call at least once before giving up

---

### DATA-1: N+1 Query Explosion in Classification List Endpoint
**File:** `api/src/sorting_hat/routes/classification.py:102-116`
**Agents:** Data Layer, Service Layer

For 20 classifications × (1 primary + 2 secondary) × ~5 ancestor queries each = **~300 SQL queries per list request**. With `limit=100`, this could hit **1,500 queries**.

The root cause is `_resolve_node_paths` → `resolve_node_path` → `get_parent_chain`, which walks up the tree one query per level.

**Fix:**
- Use the materialized `path` column to batch-resolve all ancestors in 1-2 queries
- Or pre-compute `display_path` on the classification record
- Or cache taxonomy paths (they change infrequently)

---

### DATA-2: ORM Type Mismatch — `path` Declared as `String(1000)`, Actually `ltree`
**File:** `api/src/sorting_hat/models/taxonomy.py:66`
**Agent:** Data Layer

The ORM declares `path` as `String(1000)` but the DB column is PostgreSQL `ltree`. This means:
- Alembic autogenerate will detect a perpetual diff
- ltree operators (`@>`, `<@`) don't work through the ORM
- The GiST index on `path` is unused because queries use `LIKE` instead of ltree operators

**Fix:**
- Create a custom SQLAlchemy type for `ltree`
- Use ltree operators in `get_subtree` instead of `LIKE`

---

### INFRA-1: Both Containers Run as Root
**Files:** `api/Dockerfile`, `web/Dockerfile`
**Agent:** Infrastructure

Neither Dockerfile creates or switches to a non-root user. RCE = full root inside the container.

**Fix:**
```dockerfile
RUN addgroup --system app && adduser --system --ingroup app app
USER app
```

---

### INFRA-2: Database Port and Supabase Studio Exposed in Production
**Files:** `deploy/supabase/docker-compose.yml:4-5, 71-72`
**Agent:** Infrastructure

PostgreSQL is exposed on the host. Supabase Studio (full admin UI) is exposed on port 54323 with no authentication.

**Fix:**
- Remove `ports` from production Supabase compose
- Or bind to `127.0.0.1` only
- Remove Studio from production or put it behind auth

---

### TEST-1: Near-Zero Test Coverage on Critical Paths
**Files:** `api/tests/conftest.py`, all test files
**Agent:** Testing

| Source Module | Coverage |
|---|---|
| `routes/classification.py` (3 endpoints) | ~2% — only route registration check |
| `routes/taxonomy.py` (10 endpoints) | ~2% — only route registration check |
| `services/classifier.py` (classify_url pipeline) | ~15% — only `_parse_classification` |
| `services/scraper.py` (fetch_and_extract) | ~20% — constructor + trafilatura demo |
| `services/taxonomy.py` (14 methods) | ~10% — slugify + one search_nodes path |

The `conftest.py` is empty. No async DB session fixture, no TestClient with dependency overrides, no shared mocks.

**Fix:**
1. Build conftest infrastructure (async SQLite session, TestClient, mock fixtures)
2. Test `classify_url` pipeline with mocked LLM/scraper
3. Test all 13 HTTP endpoints
4. Test `fetch_and_extract` with mocked HTTP
5. Test `TaxonomyService` CRUD methods

---

## High Findings

### SEC-4: Internal Exception Details Leaked to Clients
**File:** `api/src/sorting_hat/routes/classification.py:68`

```python
raise HTTPException(status_code=500, detail=f"Classification failed: {e}")
```

Raw exception messages (DB connection strings, file paths, LLM API errors) are returned to users.

**Fix:** Return generic message to client, log full details server-side.

---

### SEC-5: LIKE Wildcard Injection in Search
**Files:** `api/src/sorting_hat/routes/classification.py:112`, `api/src/sorting_hat/services/taxonomy.py:185-186`

User-supplied strings are wrapped in `%...%` for LIKE queries without escaping `%` and `_` wildcards. Not SQL injection, but allows query manipulation.

**Fix:** `query.replace('%', '\\%').replace('_', '\\_')` before interpolation.

---

### SEC-6: No Rate Limiting
**File:** `api/src/sorting_hat/main.py`

Each `/classify` call costs real LLM tokens and triggers outbound HTTP. No abuse protection anywhere.

**Fix:** Add `slowapi` middleware. Strict limits on classify (10/min/IP), moderate on writes, higher on reads.

---

### SVC-4: No LLM Client Timeout
**File:** `api/src/sorting_hat/llm/openai_compat.py:8`

Default OpenAI SDK timeout is 10 minutes. Two sequential LLM calls = potential 20-minute hang holding a DB session.

**Fix:** `AsyncOpenAI(api_key=..., base_url=..., timeout=60)`

---

### SVC-5: No Validation That LLM-Returned Node IDs Exist
**File:** `api/src/sorting_hat/services/classifier.py:116-117`

The LLM can hallucinate UUIDs. `primary_node_id` has a FK (will error on flush), but `secondary_node_ids` is a plain array — hallucinated IDs persist silently.

**Fix:** Look up all returned node IDs before assignment. Discard any that don't resolve.

---

### DATA-3: `secondary_node_ids` Lacks Referential Integrity
**File:** `api/src/sorting_hat/models/classification.py:35-37`

UUID array with no FK constraint. If a taxonomy node is deleted, classifications referencing it as secondary have dangling UUIDs.

**Fix:** Join table with proper FKs, or DB trigger validation, or application-level validation.

---

### DATA-4: Supabase Migrations Lag Behind Alembic
**File:** `supabase/migrations/` (2 files) vs `api/alembic/versions/` (3 files)

Alembic has `003_seed_taxonomy_nodes`. No corresponding Supabase migration. Deploy via Supabase = empty taxonomy.

**Fix:** Create matching Supabase migration. Establish sync process or choose one migration system.

---

### DATA-5: N+1 Queries in `get_parent_chain`
**File:** `api/src/sorting_hat/services/taxonomy.py:163-173`

Issues one SQL query per ancestor level. For depth-5 nodes, that's 5 round-trips.

**Fix:** Split the materialized `path` and fetch all ancestors in a single `WHERE path IN (...)` query.

---

### FE-1: No API Error Body Parsing
**File:** `web/src/lib/api.ts:11-14`

Error responses discard the body: only `response.status + statusText`. Backend error details (e.g., `{"detail": "Node not found"}`) are never shown.

**Fix:** Parse response body before throwing. Extract `detail` or `message` field.

---

### FE-2: No Error Handling in Taxonomy Page
**File:** `web/src/app/taxonomy/page.tsx:18-26, 39-42`

No `.catch()` on the node list fetch. No `try/catch` on `handleSelect`. API failures → unhandled rejections → permanent loading state.

**Fix:** Add error state, `.catch()` handlers, and user-visible error messages.

---

### FE-3: No Debounce on Taxonomy Search
**File:** `web/src/app/taxonomy/page.tsx:34-37`

Every keystroke fires an API request. Typing "firewall" = 8 requests. No `AbortController` to cancel in-flight requests.

**Fix:** 300ms debounce + `AbortController` signal on fetch.

---

### FE-4: Classification Page — Immediate GET After POST, No Polling
**File:** `web/src/app/classify/page.tsx:18-19`

`POST /classify` → immediate `GET /classify/{id}`. If classification is async, the detail will have null fields.

**Fix:** Implement polling or check a status field before displaying results.

---

### INFRA-3: No Health Checks on Any Service
**Files:** All compose files

Docker and Traefik cannot distinguish running-but-broken from healthy. Dead containers still receive traffic.

**Fix:** Add `healthcheck` to api (`/api/v1/health`) and web services.

---

### INFRA-4: No Resource Limits on Any Service
**Files:** All compose files

Memory leaks, runaway queries, or OOM can consume the entire host.

**Fix:** Add `deploy.resources.limits` (memory, CPU) to every production service.

---

### INFRA-5: `latest` Tags in Production Compose
**Files:** `docker-compose.prod.yml:3,16`

Non-reproducible deployments. No rollback capability.

**Fix:** Pin to SHA-tagged versions from CI.

---

## Medium Findings (Summary)

| ID | Area | File | Issue |
|----|------|------|-------|
| SEC-7 | Security | `main.py:49-55` | CORS `allow_methods=["*"]` + `allow_headers=["*"]` with credentials |
| SEC-8 | Security | `schemas/classification.py:9` | URL field is plain `str`, no format/scheme validation |
| SEC-9 | Security | `routes/classification.py:61` | User-controlled LLM model selection (cost abuse) |
| SEC-10 | Security | `main.py:44-46` | OpenAPI docs always exposed (production map for attackers) |
| SEC-11 | Security | `services/scraper.py:31,41` | Error messages leak network topology details |
| DATA-6 | Data | `db.py:5` | No connection pool config (`pool_pre_ping`, `pool_size`) |
| DATA-7 | Data | `db.py:5-6` | Engine never disposed on shutdown |
| DATA-8 | Data | `routes/taxonomy.py:42-50` | Fragile double-session dependency pattern |
| DATA-9 | Data | `schemas/taxonomy.py:55` | `branch` field is plain `str`, not validated against enum |
| DATA-10 | Data | `services/taxonomy.py:151-161` | `get_subtree` uses LIKE instead of ltree operators; GiST index unused |
| DATA-11 | Data | `models/classification.py:35` | No CHECK constraint enforcing max 2 secondary nodes |
| DATA-12 | Data | Various migrations | Seed migrations not idempotent; destructive downgrades |
| SVC-6 | Service | `routes/classification.py:21-40,87-98` | Duplicated node-path resolution code |
| SVC-7 | Service | `services/classifier.py:125-134` | Full taxonomy loaded on every classification (no caching) |
| SVC-8 | Service | `services/scraper.py:33-38` | `trafilatura.extract` blocks event loop (sync in async) |
| SVC-9 | Service | `services/scraper.py:40-41` | No minimum content length check (1-char content → wasted LLM call) |
| SVC-10 | Service | `routes/classification.py:50-70` | No overall pipeline timeout |
| SVC-11 | Service | `services/taxonomy.py:184-185` | LIKE metacharacters not escaped in search |
| FE-5 | Frontend | `api.ts:3-15` | No request timeout or AbortController support |
| FE-6 | Frontend | `taxonomy-tree.tsx:20-53` | No ARIA tree roles, no keyboard navigation |
| FE-7 | Frontend | `taxonomy-tree.tsx:63-69` | `childrenMap` rebuilt every render (no `useMemo`) |
| FE-8 | Frontend | `sidebar.tsx:7-9` | Emoji icons not accessible; no responsive collapse |
| FE-9 | Frontend | `classification-result.tsx:68-73` | Toggle button missing `type="button"` and `aria-expanded` |
| INFRA-6 | Infra | `pyproject.toml` | Floor versions only, no lock file |
| INFRA-7 | Infra | `web/Dockerfile:1` | `node:lts-alpine` is a floating tag |
| INFRA-8 | Infra | `entrypoint.sh:4` | Alembic migrations run at every startup as root |
| INFRA-9 | Infra | `docker-compose.prod.yml` | Missing restart policies and depends_on |
| INFRA-10 | Infra | `deploy/traefik/traefik.yml` | No rate limiting, security headers, or WAF |
| INFRA-11 | Infra | `deploy.yml:3-5` | CI only triggers on push, not PRs |
| INFRA-12 | Infra | `deploy.yml:70-86` | No Docker build cache in CI |
| TEST-2 | Test | Various | Missing edge cases in schema/parser tests |
| TEST-3 | Test | `test_classifier.py:32` | `__new__` instantiation bypasses constructor |

---

## Positive Observations

The review agents also noted several strengths worth preserving:

- **Zero `any` types in the entire frontend.** Strict TypeScript, well-defined interfaces, proper union types. Exemplary.
- **No `dangerouslySetInnerHTML` anywhere.** All dynamic content rendered via JSX text interpolation. Inherently XSS-safe.
- **Clean component architecture.** UI primitives (shadcn/ui) properly separated from domain components.
- **Correct `"use client"` boundaries.** Only components needing hooks/browser APIs are client components.
- **Well-structured API client.** Clean typed interface with proper query parameter construction.
- **Cancellation pattern in useEffect.** `cancelled` flag prevents stale state updates.
- **Strong seed tests.** The `test_seed.py` suite is thorough — verifies counts, structure, path uniqueness, SQL correctness.
- **Good materialized path design.** The ltree column enables efficient tree queries (once the ORM is fixed to use it).
- **Clean service layer separation.** Business logic in services, routing in routes, LLM abstraction clean.

---

## Recommended Fix Order

### Phase 1: Security Hardening (Do First)
1. **SEC-1** SSRF URL validation in scraper
2. **SEC-2** Authentication (API key minimum)
3. **SEC-3** Response body size limit
4. **SEC-6** Rate limiting
5. **SEC-4** Stop leaking exception details

### Phase 2: Reliability
6. **SVC-1** LLM retry logic with exponential backoff
7. **SVC-4** LLM client timeout
8. **SVC-3** Fail on null primary node
9. **SVC-5** Validate returned node IDs exist
10. **DATA-1** Fix N+1 query explosion

### Phase 3: Data Integrity
11. **DATA-2** Fix ltree type mismatch in ORM
12. **DATA-3** Add referential integrity for secondary nodes
13. **DATA-4** Sync Supabase migrations
14. **DATA-6** Configure connection pool

### Phase 4: Infrastructure
15. **INFRA-1** Non-root containers
16. **INFRA-2** Remove exposed DB port/Studio in production
17. **INFRA-3** Add health checks
18. **INFRA-5** Pin image tags

### Phase 5: Test Coverage
19. **TEST-1** Build conftest infrastructure
20. Test `classify_url` pipeline
21. Test all HTTP endpoints
22. Test scraper and LLM provider

### Phase 6: Frontend Polish
23. **FE-1** Parse API error bodies
24. **FE-2** Error handling on taxonomy page
25. **FE-3** Debounce search
26. **FE-6** Accessibility (ARIA tree roles)
