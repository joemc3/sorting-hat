# The Sorting Hat

An open, architectural taxonomy for classifying enterprise software and compute-related hardware by product capability.

## What Is This?

The Sorting Hat is a product for classifying enterprise IT products into a structured taxonomy. It consists of:

1. **A taxonomy** — ~220+ nodes across 10 governance groups with natural-language definitions at every node
2. **A taxonomy management API** — for maintaining and managing the taxonomy
3. **A classification API** — accepts a product URL, uses AI to read the page, and classifies the product into the correct taxonomy node(s)
4. **A single front end** — serves both taxonomy management and classification workflows

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

## License

TBD
