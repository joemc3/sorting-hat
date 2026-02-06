# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**The Sorting Hat** is a product for classifying enterprise software and compute-related hardware by product capability. It consists of:

1. **A taxonomy** — an open, architectural classification system (~220+ nodes across 10 governance groups) with AI-friendly definitions at every node
2. **A taxonomy management API** — for maintaining and managing the taxonomy
3. **A classification API** — accepts a product URL, uses AI to read the page, and classifies the product into the correct taxonomy node(s)
4. **A single front end** — serves both taxonomy management and classification workflows

The taxonomy research in `research/` is the foundation. Everything else is built on top of it.

**We write production code. Always.** There are no phases, no MVPs, no "fix it later." This is one product with one deliverable.

## Repository Structure

### Research (taxonomy foundation)
- `research/Draft v0.2 - Taxonomy Structure.md` — The canonical taxonomy: design principles, governance groups, full tree (Software + Computing Hardware), edge cases table, scope boundaries, and changelog
- `research/Research - Existing IT Taxonomy Landscape.md` — Assessment of existing taxonomies (G2, TBM, TOGAF, etc.) and rationale for the hybrid approach
- `research/Taxonomy Definitions - Complete Reference.md` — Natural-language definitions for every taxonomy node, written specifically for AI classification matching

## Key Taxonomy Concepts

- **10 Governance Groups** form Level 2 and map to organizational standards/governance teams
- **Level 1** splits into **Software** and **Computing Hardware** — these branches never merge
- **Classify by capability, not delivery model** — SaaS vs on-prem is irrelevant; what the product *does* determines placement
- **Multi-category classification** — exactly ONE primary category (governance ownership), up to TWO secondary categories (cross-functional visibility)
- **Definitions at every node** — the AI classification system matches product webpages against these definitions
- **No product catalog** — the taxonomy classifies products but doesn't maintain a list of them
- **No financial layers** — purely architectural, not for cost/spend management
- **Flexible depth** — branches go 3-5 levels deep following domain complexity, not arbitrary rules

## Working with the Taxonomy

When modifying the taxonomy:
- Keep the three research documents in sync — structural changes in the Draft must be reflected in the Definitions reference
- Preserve YAML frontmatter (tags, created/modified dates) at the top of each file
- Update the edge cases table when adding categories that affect classification boundaries
- Definitions must follow the established format: what products DO, distinguishing characteristics, inclusions, exclusions
- Respect the max-2-secondaries rule; if many products need more, the structure needs refinement
