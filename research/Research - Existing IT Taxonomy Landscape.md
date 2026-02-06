---
created: 2026-02-05
modified: 2026-02-05
tags:
  - status/active
  - type/reference
  - project/sorting-hat
  - ai/llm
  - doc/spec
---
# Research: Existing IT Taxonomy Landscape

## What We're Building

A pure architectural taxonomy for classifying **all software** and **compute-related hardware** (networking, servers, storage — not physical/mechanical) in an enterprise. The taxonomy needs:

- Clear definitions at every node so AI can classify unknown products by reading a URL
- Roughly 9-10 high-level groups at the 2nd or 3rd tier that map to governance/standards teams
- Examples of governance groups: Application Development Tools, Engineering Tools (PLM/CAD/CAM), Networking, Desktop Productivity, Collaboration Tools & Hardware
- No financial layers, cost centers, or spend categories
- No pre-populated product catalog (tried NIST CPE — too many holes, naming inconsistencies were a nightmare)
- Free or open source only — zero budget beyond future AI token costs

The end goal (future phase): feed the taxonomy + a product URL to an AI, and it classifies the product into the right bucket.

---

## What Exists: The Honest Assessment

**There is no single, free, downloadable taxonomy that does this out of the box.** Everything is either too broad, too abstract, too messy, or paywalled. But there are strong building blocks.

---

## Tier 1: Strongest Candidates

### G2 Category Structure (Software Side)
- **What it is:** 2,100+ software categories in a parent-child hierarchy, 2-3 levels deep
- **Why it matters:** Every category has a written market definition — exactly what AI needs for classification
- **Access:** Publicly browsable at g2.com/categories. No structured download without a developer/partner relationship.
- **Coverage:** Software and SaaS only. Zero hardware.
- **Note:** G2 acquired Capterra, GetApp, and Software Advice from Gartner in Jan 2026 — consolidating into the largest software taxonomy available
- **Verdict:** Best software taxonomy structure out there. Would need to extract the category tree and definitions from their public pages or negotiate API access.

### TBM Taxonomy v5.0.1 (Governance Structure)
- **What it is:** Technology Business Management framework with four layers and "technology towers"
- **Why it matters:** The tower layer maps naturally to ~9-10 governance groups
- **Access:** Free download from tbmcouncil.org/taxonomy/
- **Limitation:** Financial/cost layers are deeply baked in; hard to cleanly separate the architectural classification from the spend management purpose
- **Verdict:** Useful as inspiration for the governance-group tier, but not a direct fit for a pure architectural taxonomy.

---

## Tier 2: Useful for Hardware / Infrastructure Side

### TOGAF Technology Reference Model (TRM)
- **What it is:** Organizes platform services into categories: Data Management, Network Services, OS Services, Graphics/Imaging, Transaction Processing, etc.
- **Access:** Free for non-commercial use from opengroup.org
- **Limitation:** Defines service layers, not product categories. Too abstract to use directly.
- **Verdict:** Good conceptual backbone for how to think about the hardware/infrastructure groupings.

### ArchiMate Technology Layer
- **What it is:** Modeling language with clean technology element types: Nodes, Devices, System Software, Communication Networks, Artifacts, Technology Services
- **Access:** Free specification from The Open Group
- **Limitation:** It's a modeling vocabulary, not a classification tree with definitions
- **Verdict:** Informs how to structure hardware categories conceptually.

### FEA Technical Reference Model (US Government)
- **What it is:** Service Areas -> Categories -> Standards. Covers infrastructure, networking, data management.
- **Access:** Free (US government publication). PDF from reginfo.gov.
- **Limitation:** Dated (2007). More about standards/protocols than product types.
- **Verdict:** Decent reference for infrastructure classification, but needs significant modernization.

### DMTF CMDBf (CI Type Taxonomy)
- **What it is:** Defines Configuration Item types: Software, Hardware, Network, Storage, Business
- **Access:** Free PDF from dmtf.org
- **Limitation:** Very high-level — only 5 top-level types, not deep enough on its own
- **Verdict:** Good top-level framing, but you'd need to build all the depth below it.

---

## Tier 3: Investigated but Ruled Out

| Source | Why It Doesn't Fit |
|--------|-------------------|
| **NIST CPE Dictionary** | Product catalog, not a taxonomy. Too many holes, naming inconsistencies. Already tried. |
| **UNSPSC** | Covers everything from uranium to umbrellas. Pruning to just IT would be massive effort. |
| **Wikidata / DBpedia** | Community-driven, documented class hierarchy problems (cycles, inconsistent depth, class-instance confusion). |
| **eCl@ss** | Very detailed (45,000 classes) but requires paid license for download. Free to search only. |
| **Flexera Technopedia** | Best commercial option (3.5M products, GraphQL API) but requires Flexera licensing. Product catalog, not just taxonomy. |
| **IDC Taxonomy** | ~120 technologies in a well-structured hierarchy. Proprietary — requires IDC subscription. |
| **Forrester ICT Taxonomy** | Behind paywall. Designed for market sizing, not product classification. |
| **ITIL v4 CI Types** | 6 high-level types. Requires AXELOS licensing. Not granular enough. |
| **COBIT** | Governance-focused, doesn't prescribe a technology taxonomy. Proprietary. |
| **Schema.org** | Has a software types profile on GitHub but shallow. Not IT-specific enough. |
| **YAGO 4** | Cleaner than Wikidata (~95% precision) but still not purpose-built for IT. |
| **Gartner Peer Insights** | 500+ software categories browsable publicly, but not downloadable as structured data. |

---

## Tier 4: Open-Source Frameworks (Not Pre-Populated)

These are classification *frameworks* — they give you a structure to build in, but don't come with a ready-made IT taxonomy:

- **OWASP Open Asset Model** — Best for security/network asset types. GitHub: owasp-amass/open-asset-model
- **Amberdata ARC** — Flexible, non-hierarchical classification with JSON schema. GitHub: amberdata/arc
- **CIS Controls v8.1** — 6 asset classes (Devices, Software, Data, Users, Networks, Documentation). Free from cisecurity.org.

---

## Recommended Path Forward

### The Hybrid Approach
1. **Governance layer (your 9-10 groups):** Define these yourself based on how your org wants to govern. Use TBM towers and G2's top-level parent categories as reference for where to draw the lines.
2. **Software taxonomy:** Extract G2's category tree and definitions as the backbone. It's the most complete, well-defined, publicly visible structure available.
3. **Hardware taxonomy:** Build a lighter-weight tree informed by TOGAF TRM service categories and ArchiMate technology types, plus practical categories for networking gear, compute infrastructure, storage, endpoint devices, and collaboration hardware.
4. **Definitions at every node:** Critical for the future AI classification step. G2 already has these for software. You'd need to write them for hardware categories and the governance tier.

### Why This Works for AI Classification Later
- G2's category definitions are written in natural language describing what products in that category do — which is exactly what an LLM needs to match a product webpage against
- A clear hierarchical path (Governance Group -> Category -> Subcategory) with definitions at each level gives the AI a decision tree to walk
- The taxonomy stays product-agnostic (no catalog to maintain) while being specific enough to classify new products on the fly

---

## Open Questions for Next Session
- Should we start by extracting G2's category tree, or draft the governance groups first?
- How deep should the taxonomy go? 3 levels? 4?
- Do collaboration tools and their hardware (conference room AV, etc.) live together or separate?
- Where do cloud/SaaS platform services land vs. the software they enable?
- Should there be a "cross-cutting" layer for things like security tools that span multiple governance groups?

---

## Key Links
- G2 Categories: https://www.g2.com/categories
- TBM Taxonomy: https://www.tbmcouncil.org/taxonomy/
- TOGAF TRM: https://pubs.opengroup.org/togaf-standard/reference-models/trm.html
- ArchiMate Technology Layer: https://pubs.opengroup.org/architecture/archimate3-doc/ch-Technology-Layer.html
- DMTF CMDBf: https://www.dmtf.org/standards/cmdbf
- FEA TRM: https://www.reginfo.gov/public/jsp/Utilities/FEA_CRM_v23_Final_Oct_2007_Revised.pdf
- OWASP Open Asset Model: https://github.com/owasp-amass/open-asset-model
- CIS Controls Asset Classes: https://www.cisecurity.org/insights/white-papers/guide-to-asset-classes-cis-critical-security-controls-v8-1
