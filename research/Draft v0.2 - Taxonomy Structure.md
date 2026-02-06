---
created: 2026-02-05
modified: 2026-02-05
tags:
  - status/draft
  - type/project
  - project/sorting-hat
  - doc/spec
---
# The Sorting Hat: Enterprise IT Taxonomy — Draft v0.2

> **Purpose:** An open, architectural taxonomy for classifying enterprise software and compute-related hardware by product capability. No financial layers. No product catalog. Clear definitions at every node for AI-driven classification.
>
> **What changed from v0.1:** Added multi-category classification (primary + secondary). Split Business Applications into Business Operations and Customer & Revenue Technology. Added missing categories (communications APIs, content management, media production, e-commerce). Resolved DevOps/IaC boundary. Expanded definitions throughout.

---

## Design Principles

### 1. Classify by Capability, Not Delivery Model
A product is classified by what it *does*, not how it's delivered. A SaaS CRM and an on-prem CRM both go under Customer & Revenue Technology > CRM. Cloud, on-prem, hybrid — irrelevant to classification.

### 2. Hardware and Software Are Always Separate Branches
Level 1 splits into **Software** and **Computing Hardware**. A governance group may own nodes in one or both branches, but the branches never merge.

### 3. Governance Groups Are the Tree
The ~10 governance groups are literally the Level 2 nodes. This keeps the taxonomy directly actionable — the tree structure IS the governance structure. Organizations adopting this taxonomy can rename groups to match their org, but the tree stays intact.

### 4. Flexible Depth
Some branches go 3 levels, others go 4-5. Developer tooling is deep and branching; digital signage is two levels. Depth follows the domain, not an arbitrary rule.

### 5. Multi-Category Classification (Primary + Secondary)

Products exist in the real world across domain boundaries. This taxonomy supports that through primary and secondary classification:

**Rules:**
- Every product gets exactly **ONE primary category**. This determines governance ownership.
- A product may have up to **TWO secondary categories** for cross-functional visibility.
- **Primary** = "Which governance team owns the standard, evaluation, and lifecycle for this product?"
- **Secondary** = "Which other governance teams have a legitimate interest or need visibility?"
- Secondary classification **does not transfer governance authority**. It's informational.
- If a product cannot be meaningfully classified without a secondary, that's fine — many products genuinely span domains.
- If *most* products in a category need secondaries, that's a signal the taxonomy structure needs refinement.

**Examples:**
| Product | Primary | Secondary | Rationale |
|---------|---------|-----------|-----------|
| Terraform | IT Ops > Config Mgmt & Automation | App Dev > Infrastructure & Platform Tooling | Ops owns the standard; platform engineers are primary users |
| Datadog | IT Ops > Monitoring & Observability | Data & Analytics > BI & Visualization | Ops owns it; analytics teams use dashboards |
| Palo Alto PA-series | Security > Firewall Appliances | Networking > (visibility) | Security owns all security-purposed hardware |
| Figma | Engineering & Design > UX & Digital Design | Collaboration > (visibility) | Design team owns it; collaborative features are secondary |
| Notion | Collaboration > Knowledge Mgmt & Wikis | End-User Computing > (visibility) | Collaboration owns it; also used as personal productivity |
| ServiceNow | IT Ops > ITSM | Business Operations > (visibility) | IT Ops owns the platform; expanding into business workflows |

### 6. Definitions at Every Node
Every node in the taxonomy — from Level 2 governance groups down to the deepest leaf — carries a natural-language definition describing what products in that category do. These definitions are the primary input for AI-driven classification.

---

## The 10 Governance Groups

| # | Governance Group | SW | HW | Scope |
|---|-----------------|----|----|-------|
| 1 | Application Development & Platform | Yes | — | Building, testing, deploying, and maintaining software; developer tools and platforms |
| 2 | Business Operations | Yes | — | Back-office systems: ERP, finance, HR, procurement, supply chain, legal, compliance |
| 3 | Customer & Revenue Technology | Yes | — | Front-office systems: CRM, marketing, sales enablement, e-commerce, customer success |
| 4 | Data & Analytics | Yes | — | Collecting, storing, processing, analyzing, and visualizing data; AI/ML platforms |
| 5 | Collaboration & Communication | Yes | Yes | Enabling people to work together and communicate, both software and physical devices |
| 6 | End-User Computing | Yes | Yes | Individual productivity software and personal work devices |
| 7 | Security | Yes | Yes | Protecting information, systems, and infrastructure from threats |
| 8 | IT Operations & Infrastructure | Yes | Yes | Managing, monitoring, and maintaining IT systems; compute and storage hardware |
| 9 | Engineering & Design | Yes | — | Specialized tools for engineering, manufacturing, design, and media production |
| 10 | Networking | Yes | Yes | Connecting systems, managing network infrastructure, enabling device communication |

---

## Full Taxonomy Tree

### SOFTWARE

#### 1. Application Development & Platform
> *Tools and technologies for building, testing, deploying, and maintaining software applications and platforms.*

- **IDEs & Code Editors** — Integrated development environments and lightweight code editors for writing, debugging, and managing code.
  - Cloud-Based IDEs
  - Desktop IDEs
  - Specialized / Embedded IDEs
- **Programming Languages & Runtimes** — Language interpreters, compilers, virtual machines, and runtime environments that execute application code.
- **Frameworks & Libraries** — Reusable code foundations providing structure and common functionality for application development.
  - Frontend Frameworks
  - Backend Frameworks
  - Mobile Frameworks
  - Full-Stack Frameworks
- **Version Control & Source Management** — Systems for tracking code changes, branching, merging, and collaborative source code management.
- **CI/CD & Build Automation** — Continuous integration, continuous delivery pipelines, and build automation systems that compile, test, and deploy code.
- **Testing & Quality Assurance** — Tools for verifying software correctness, performance, and quality.
  - Unit & Integration Testing Frameworks
  - Performance & Load Testing
  - Code Quality & Static Analysis
  - Test Management Platforms
- **API Development & Management** — Tools for designing, building, documenting, testing, securing, and managing application programming interfaces.
  - API Gateways
  - API Design & Documentation
  - API Testing & Mocking
- **Low-Code / No-Code Platforms** — Visual development environments enabling application creation with minimal or no hand-written code.
- **Package & Dependency Management** — Registries, package managers, and artifact repositories for managing software dependencies.
- **Containerization & Orchestration** — Tools for building, running, and orchestrating container-based workloads.
  - Container Runtimes & Engines
  - Container Orchestration Platforms
  - Container Registries
- **Infrastructure & Platform Tooling** — Developer-facing tools for provisioning and managing cloud and infrastructure resources through code.
  - Infrastructure-as-Code (IaC) Authoring
  - Platform Engineering Tools
  - Serverless Frameworks
- **Communications & Messaging APIs** — Developer platforms and SDKs for embedding voice, video, SMS, email, and messaging capabilities into applications.
- **Developer Collaboration & Documentation** — Developer-audience code review tools, internal documentation platforms, and dev-specific workflow tools.
- **AI-Assisted Development** — AI coding assistants, code generation tools, and intelligent development aids.

#### 2. Business Operations
> *Software supporting back-office business functions: finance, human resources, procurement, supply chain, legal, and enterprise-wide operational systems.*

- **Enterprise Resource Planning (ERP)** — Integrated suites managing finance, operations, HR, and supply chain in a unified system.
- **Financial & Accounting** — Dedicated financial management, general ledger, billing, invoicing, and accounting systems.
  - Accounts Payable / Accounts Receivable
  - Expense Management
  - Budgeting & Forecasting
  - Tax Management
  - Revenue Recognition
- **Human Capital Management (HCM)** — Systems for managing the employee lifecycle from recruiting through retirement.
  - Recruiting & Talent Acquisition
  - Payroll & Benefits Administration
  - Performance Management
  - Learning & Development (LMS)
  - Workforce Management & Scheduling
  - Employee Experience Platforms
- **Procurement & Sourcing** — Tools for managing purchasing, vendor selection, contract negotiation, and supplier relationships.
- **Supply Chain Management (SCM)** — Software for logistics, inventory, warehouse operations, and supply chain planning.
  - Warehouse Management (WMS)
  - Transportation Management (TMS)
  - Inventory Management
  - Demand Planning & Forecasting
- **Legal & Compliance** — Contract lifecycle management, compliance tracking, e-discovery, and regulatory management tools.
- **Governance, Risk & Compliance (GRC)** — Enterprise risk assessment, policy management, audit management, and regulatory compliance platforms.

#### 3. Customer & Revenue Technology
> *Software supporting front-office functions: sales, marketing, customer engagement, e-commerce, and revenue generation.*

- **Customer Relationship Management (CRM)** — Systems for managing customer interactions, sales pipelines, accounts, and customer data.
  - Sales Force Automation
  - Customer Service & Support
  - Contact Center Software
  - Customer Data Platforms (CDP)
- **Marketing Technology** — Platforms for planning, executing, measuring, and optimizing marketing campaigns and customer engagement.
  - Marketing Automation
  - Email Marketing
  - Account-Based Marketing (ABM)
  - Social Media Management
  - SEO & SEM Tools
  - Advertising & Demand Generation
- **Sales Enablement & Operations** — Tools that support sales teams with content, training, engagement tracking, and pipeline analytics.
  - Sales Engagement Platforms
  - Configure-Price-Quote (CPQ)
  - Sales Intelligence & Prospecting
  - Revenue Operations
- **E-Commerce & Digital Storefronts** — Platforms for online selling, product catalog management, cart/checkout, and order management.
- **Content Management & Web Publishing** — Systems for creating, managing, and publishing digital content to websites and digital channels.
  - Web Content Management (CMS)
  - Headless CMS
  - Digital Asset Management (DAM)
  - Digital Experience Platforms (DXP)
- **Customer Success & Retention** — Tools for monitoring customer health, managing renewals, reducing churn, and driving adoption.
- **Survey & Feedback** — Platforms for collecting, analyzing, and acting on customer and market feedback.

#### 4. Data & Analytics
> *Technologies for collecting, storing, processing, analyzing, and visualizing data to derive insights and enable data-driven decisions.*

- **Databases** — Systems for persistent data storage and retrieval, optimized for various data models and access patterns.
  - Relational / SQL Databases
  - NoSQL / Document Databases
  - Graph Databases
  - Time-Series Databases
  - In-Memory / Caching Databases
  - Vector Databases
- **Data Warehouses & Data Lakes** — Centralized repositories for structured and unstructured data optimized for analytical workloads at scale.
  - Cloud Data Warehouses
  - Data Lakehouse Platforms
  - On-Premises Data Warehouses
- **Data Integration & ETL/ELT** — Tools for extracting, transforming, loading, and moving data between systems.
  - ETL/ELT Platforms
  - Data Pipeline Orchestration
  - Data Replication & Change Data Capture (CDC)
  - iPaaS / Integration Platforms
- **Business Intelligence & Visualization** — Reporting, dashboarding, and visual analytics tools for business users to explore and present data.
- **Advanced Analytics & Data Science** — Platforms for statistical analysis, machine learning, and data science workflows.
  - ML/AI Development Platforms
  - Notebook & Experimentation Environments
  - MLOps & Model Management
  - Statistical Analysis Tools
- **Data Governance & Quality** — Master data management, data cataloging, lineage tracking, and data quality monitoring.
  - Data Catalogs & Metadata Management
  - Data Quality & Profiling
  - Data Lineage & Impact Analysis
  - Master Data Management (MDM)
- **Streaming & Event Processing** — Real-time data ingestion, stream processing, and event-driven data architectures.

#### 5. Collaboration & Communication (Software)
> *Software enabling people to work together, communicate, and share knowledge across teams and organizations.*

- **Unified Communications Platforms** — Integrated platforms combining messaging, voice, video, and presence in a single system.
- **Email & Calendar** — Email clients, email servers, and calendaring/scheduling systems.
- **Instant Messaging & Team Chat** — Real-time text-based communication platforms for teams.
- **Video Conferencing Software** — Applications for virtual meetings, webinars, and video calls.
- **Project & Work Management** — Tools for planning, tracking, and managing projects, tasks, and cross-functional workflows.
  - Project Management
  - Agile & Kanban Boards
  - Resource Planning & Allocation
  - Portfolio Management
- **Knowledge Management & Wikis** — Internal knowledge bases, wikis, and organizational documentation platforms.
- **Document Collaboration** — Real-time co-authoring, document sharing, and version management tools.
- **Social Intranet & Employee Engagement** — Internal communication platforms, company intranets, and employee engagement tools.
- **Digital Whiteboarding & Visual Collaboration** — Virtual whiteboards and visual brainstorming tools for real-time or asynchronous collaboration.

#### 6. End-User Computing (Software)
> *Software for individual productivity, daily work, and end-user experience on personal computing devices.*

- **Office Productivity Suites** — Integrated suites for word processing, spreadsheets, and presentations.
- **PDF & Document Tools** — PDF creation, editing, annotation, conversion, and digital signature tools.
- **Web Browsers** — Internet browsers and browser-based productivity extensions.
- **Note-Taking & Personal Knowledge Management** — Personal note-taking, bookmarking, clipping, and information organization applications.
- **File Management & Cloud Sync** — File explorers, cloud storage sync clients, and local file management tools.
- **Remote Desktop & Virtual Desktop Clients** — Client software for accessing remote desktops, VDI sessions, or DaaS environments.
- **Desktop Utilities & System Tools** — Clipboard managers, screenshot tools, personal password managers, launchers, and desktop automation utilities.
- **Printing & Scanning Software** — Drivers, print management software, and scanning utilities.
- **Accessibility Tools** — Screen readers, magnification, voice control, and other assistive technologies for computing.

#### 7. Security (Software)
> *Software for protecting information, systems, networks, and infrastructure from threats, unauthorized access, and data loss.*

- **Identity & Access Management (IAM)** — Authentication, authorization, identity governance, and access lifecycle management.
  - Multi-Factor Authentication (MFA)
  - Single Sign-On (SSO)
  - Privileged Access Management (PAM)
  - Directory & Identity Providers
  - Identity Governance & Administration (IGA)
- **Endpoint Security** — Antivirus, EDR/XDR, and endpoint protection platforms that defend individual devices.
- **Network Security Software** — Software-based firewalls, intrusion detection/prevention, and network traffic analysis.
- **SIEM & Security Analytics** — Centralized log collection, threat correlation, alerting, and security analytics platforms.
- **Security Orchestration & Automation (SOAR)** — Automated incident response, playbook execution, and security workflow orchestration.
- **Vulnerability Management** — Scanning, assessment, prioritization, and remediation tracking for security vulnerabilities.
- **Data Loss Prevention (DLP)** — Tools for monitoring, detecting, and preventing unauthorized movement or exfiltration of sensitive data.
- **Email & Messaging Security** — Anti-phishing, anti-spam, email encryption, and secure email gateway products.
- **Cloud Security** — CASB, CSPM, CWPP, and security tools specific to cloud infrastructure and SaaS environments.
- **Encryption & Key Management** — Data encryption, certificate management, and cryptographic key lifecycle tools.
- **Application Security** — SAST, DAST, SCA, and tools for securing application code and dependencies.
- **Threat Intelligence** — Platforms aggregating, analyzing, and distributing threat data for proactive defense.
- **Security Awareness & Training** — Phishing simulation, security training content, and employee awareness platforms.

#### 8. IT Operations & Infrastructure (Software)
> *Software for managing, monitoring, automating, and maintaining IT systems, services, and infrastructure at scale.*

- **IT Service Management (ITSM)** — Service desks, ticketing systems, incident/problem/change management aligned to ITIL practices.
- **Monitoring & Observability** — Tools for watching the health, performance, and behavior of infrastructure and applications.
  - Infrastructure Monitoring
  - Application Performance Monitoring (APM)
  - Log Management & Analysis
  - Distributed Tracing
  - Synthetic Monitoring
- **Configuration Management & Automation** — Tools for automating infrastructure provisioning, configuration, and operational workflows at the operations layer.
  - Configuration Management Engines
  - IT Process Automation / Runbook Automation
  - Patch Management
- **Backup & Disaster Recovery** — Data backup, replication, archival, and disaster recovery orchestration solutions.
- **Virtualization & Hypervisors** — Software for creating and managing virtual machines and virtual infrastructure.
- **Cloud Management & Governance** — Multi-cloud management, cloud governance, cost optimization, and cloud operations platforms.
- **IT Asset Management (ITAM)** — Hardware and software inventory tracking, license management, and lifecycle management.
- **Remote Monitoring & Management (RMM)** — Tools for remotely managing, monitoring, and maintaining distributed endpoint and server fleets.
- **CMDB & Service Mapping** — Configuration management databases and automated service dependency mapping.
- **Mobile Device Management (MDM) / Unified Endpoint Management (UEM)** — Platforms for enrolling, configuring, securing, and managing mobile devices and diverse endpoints.

#### 9. Engineering & Design
> *Specialized software for engineering disciplines, manufacturing, product design, creative production, and scientific research.*

- **Computer-Aided Design (CAD)** — 2D and 3D design and drafting tools for mechanical, architectural, and structural design.
  - Mechanical CAD
  - Architectural & Building Information Modeling (BIM)
  - Electrical & PCB Design
- **Computer-Aided Manufacturing (CAM)** — Software for generating CNC toolpaths and controlling manufacturing equipment.
- **Computer-Aided Engineering (CAE)** — Simulation, finite element analysis (FEA), computational fluid dynamics (CFD), and structural analysis tools.
- **Product Lifecycle Management (PLM)** — End-to-end management of a product's lifecycle from concept through retirement, including engineering change management.
- **Electronic Design Automation (EDA)** — IC layout, chip design, FPGA development, and semiconductor design tools.
- **UX & Digital Design** — User experience design, UI prototyping, wireframing, and interaction design tools.
- **3D Modeling, Rendering & Visualization** — 3D content creation, photorealistic rendering, and immersive visualization beyond CAD.
- **Media & Content Production** — Video editing, audio production, motion graphics, and post-production tools for professional media creation.
  - Video Editing & Post-Production
  - Audio Production & Engineering
  - Motion Graphics & Animation
  - Graphic Design & Illustration
- **Geographic Information Systems (GIS)** — Spatial data analysis, mapping, geospatial visualization, and location intelligence tools.
- **Scientific & Research Software** — Laboratory information management (LIMS), scientific computation, research data management, and specialized analysis tools.

#### 10. Networking (Software)
> *Software for configuring, managing, monitoring, and optimizing network infrastructure and connectivity.*

- **Software-Defined Networking (SDN)** — Controllers and platforms for abstracting and centrally managing network infrastructure through software.
- **Network Monitoring & Management** — Tools for monitoring network health, performance, traffic flows, and device availability.
- **DNS, DHCP & IP Address Management (DDI)** — Tools for managing domain name resolution, dynamic host addressing, and IP address allocation.
- **Network Configuration & Change Management** — Automated network device configuration, compliance auditing, and change tracking.
- **SD-WAN** — Software-defined wide-area networking platforms for optimizing branch and multi-site WAN connectivity.
- **Network Access Control (NAC)** — Policy-based enforcement of device authentication and network admission.
- **Wi-Fi Management & Wireless Planning** — Wireless network planning, deployment, optimization, and management tools.
- **VPN & Secure Remote Access** — Virtual private network software and zero-trust network access (ZTNA) solutions.
- **Network Automation & Orchestration** — Platforms for automating complex multi-vendor network operations and workflows.

---

### COMPUTING HARDWARE

#### 5. Collaboration & Communication (Hardware)
> *Physical devices enabling in-person and hybrid collaboration, conferencing, and organizational communication.*

- **Video Conferencing Systems** — Room-based conferencing units, video bars, and integrated audiovisual systems.
  - Large Room Systems
  - Huddle / Small Room Devices
  - Personal Video Devices (webcams, desktop units)
- **Audio Conferencing Devices** — Speakerphones, conference phones, and room microphone/speaker arrays.
- **Interactive Displays & Whiteboards** — Touch-enabled displays and digital whiteboard hardware for in-room collaboration.
- **Room Scheduling & Control Panels** — Wall-mounted or tabletop panels for booking rooms and controlling AV equipment.
- **Digital Signage Hardware** — Displays, media players, and controllers for informational, wayfinding, or broadcast signage.
- **Telephony Hardware** — Physical PBX systems, VoIP handsets, and telephony gateway devices.

#### 6. End-User Computing (Hardware)
> *Physical devices used by individuals for daily work and personal productivity.*

- **Laptops** — Portable computing devices with integrated display, keyboard, and battery.
  - Standard Business Laptops
  - Mobile Workstations
  - Rugged / Field Laptops
  - Chromebooks & Education Devices
- **Desktops** — Stationary computing devices for office and workstation use.
  - Standard Business Desktops
  - High-Performance Workstations
  - All-in-One PCs
  - Mini / Micro PCs
- **Thin & Zero Clients** — Minimal endpoint devices relying on centralized server-side processing (VDI/DaaS).
- **Monitors & Displays** — External displays, multi-monitor setups, and specialized displays for workstation use.
- **Peripherals & Accessories** — Keyboards, mice, trackpads, docking stations, USB hubs, headsets, and other input/output devices.
- **Mobile Devices** — Smartphones and tablets deployed, managed, and secured by the organization.
- **Printers, Scanners & Multifunction Devices** — Network and local printing, scanning, and copying devices.

#### 7. Security (Hardware)
> *Physical devices dedicated to protecting networks, data, and systems from threats and unauthorized access.*

- **Firewall Appliances** — Dedicated hardware for network perimeter defense and traffic inspection.
  - Next-Generation Firewalls (NGFW)
  - Unified Threat Management (UTM) Appliances
- **Intrusion Detection / Prevention Appliances (IDS/IPS)** — Hardware for real-time detection and blocking of malicious network activity.
- **Hardware Security Modules (HSMs)** — Tamper-resistant devices for cryptographic key management, digital signing, and secure processing.
- **Network Taps & Packet Brokers** — Hardware for passively capturing and distributing network traffic for security analysis.
- **Biometric & Physical Access Devices** — Fingerprint readers, smart card readers, badge scanners, and biometric terminals integrated with IT identity systems.

#### 8. IT Operations & Infrastructure (Hardware)
> *Physical compute, storage, and data center infrastructure supporting enterprise IT operations.*

- **Servers** — Hardware platforms providing compute resources for enterprise applications, services, and workloads.
  - Rack-Mount Servers
  - Blade Servers & Chassis
  - Tower Servers
  - GPU / Accelerator Servers
  - Edge Compute Servers
  - Mainframes
- **Storage Systems** — Dedicated hardware for persistent enterprise data storage.
  - Storage Area Network (SAN) Arrays
  - Network-Attached Storage (NAS)
  - All-Flash / Solid-State Arrays
  - Hybrid Storage Arrays
  - Tape Libraries & Archive Storage
  - Hyper-Converged Infrastructure (HCI)
- **Data Center Infrastructure** — Physical infrastructure supporting compute and storage environments.
  - Server Racks & Enclosures
  - Uninterruptible Power Supplies (UPS)
  - Power Distribution Units (PDU)
  - KVM Switches & Console Servers
  - Environmental Monitoring (temperature, humidity, airflow)
  - Cooling Systems (CRAC, in-row cooling)

#### 10. Networking (Hardware)
> *Physical devices that provide network connectivity and enable communication between systems.*

- **Switches** — Devices forwarding data packets between network-connected devices based on MAC or IP addresses.
  - Access Switches (Layer 2)
  - Core / Distribution Switches (Layer 3)
  - Data Center / Top-of-Rack Switches
  - Industrial / Ruggedized Switches
  - PoE (Power over Ethernet) Switches
- **Routers** — Devices routing data between different networks using IP-based forwarding.
  - Enterprise / Campus Routers
  - Branch / Edge Routers
  - Core / Backbone Routers
- **Wireless Infrastructure** — Devices providing wireless network connectivity.
  - Wireless Access Points
  - Wireless LAN Controllers
  - Wi-Fi 6/6E/7 Access Points
- **Load Balancers & Application Delivery Controllers** — Hardware appliances distributing traffic across servers and optimizing application delivery.
- **Optical Network Terminals (ONTs) & Modems** — Devices terminating carrier connections and converting signals for local area network use.
- **WAN Optimization Appliances** — Hardware accelerating and optimizing traffic across wide-area networks.
- **Structured Cabling & Connectivity** — Patch panels, fiber optic infrastructure, media converters, and transceivers (SFP/QSFP).

---

## Edge Cases & Classification Logic

| Product / Category | Primary | Secondary | Rationale |
|-------------------|---------|-----------|-----------|
| Terraform | IT Ops > Config Mgmt & Automation | App Dev > Infrastructure & Platform Tooling | Ops governs infrastructure provisioning; devs author the code |
| Ansible | IT Ops > Config Mgmt & Automation | App Dev > Infrastructure & Platform Tooling | Same pattern as Terraform — ops-owned, dev-used |
| Kubernetes | App Dev > Containerization & Orchestration | IT Ops > (visibility) | Platform/dev teams typically own K8s; ops has interest |
| Docker Desktop | App Dev > Container Runtimes & Engines | — | Developer-local tooling, clean fit |
| Datadog | IT Ops > Monitoring & Observability | Data & Analytics > (visibility) | Ops owns monitoring; analytics teams consume dashboards |
| Twilio | App Dev > Communications & Messaging APIs | — | Developer platform for embedded communications |
| WordPress (enterprise) | Customer & Revenue > Content Management & Web Publishing | — | Customer-facing content platform |
| Notion | Collaboration > Knowledge Mgmt & Wikis | End-User Computing > (visibility) | Organizational knowledge tool with personal productivity overlap |
| Figma | Engineering & Design > UX & Digital Design | Collaboration > (visibility) | Design tool primary; collaboration features secondary |
| Miro | Collaboration > Digital Whiteboarding | Engineering & Design > (visibility) | Primary use is collaborative brainstorming; design is secondary |
| ServiceNow | IT Ops > ITSM | Business Operations > (visibility) | ITSM platform with expanding business modules |
| Palo Alto PA-series | Security HW > Firewall Appliances | Networking > (visibility) | Security governs all security-purposed hardware |
| Ubiquiti UniFi Dream Machine | Networking HW > Routers | Security > (visibility) | Network appliance primary; built-in IDS is secondary |
| Salesforce | Customer & Revenue > CRM | — | Clean fit, no secondary needed |
| HubSpot | Customer & Revenue > Marketing Technology | Customer & Revenue > CRM | Marketing-first platform with CRM module |
| Adobe Creative Cloud | Engineering & Design > Media & Content Production | — | Creative/design tooling |
| DaVinci Resolve | Engineering & Design > Media & Content Production > Video Editing | — | Clean fit under media production |
| Varonis | Security > DLP | Data & Analytics > Data Governance | Data security primary; data governance visibility |
| Bloomberg Terminal | Business Operations > Financial & Accounting | Data & Analytics > (visibility) | Financial data/trading platform; analytics is secondary function |
| Arduino boards | *See IoT note below* | Engineering & Design > (possible) | Prototyping hardware — scope question |
| SaaS CRM (any) | Customer & Revenue > CRM | — | Classify by function, not delivery model |
| AWS / Azure / GCP (as platform) | IT Ops > Cloud Management & Governance | — | Cloud platform management is infrastructure |
| Jira | Collaboration > Project & Work Management | App Dev > Developer Collaboration | Cross-functional PM tool often used heavily by dev teams |
| GitHub Issues | App Dev > Developer Collaboration | Collaboration > (visibility) | Dev-audience workflow tool |
| RingCentral | Collaboration > Unified Communications | — | Clean fit |
| Power BI | Data & Analytics > BI & Visualization | — | Clean fit |
| CrowdStrike Falcon | Security > Endpoint Security | — | Clean fit |
| Enterprise password manager (1Password Business) | Security > IAM | — | Credential management is IAM |
| Personal password manager | End-User Computing > Desktop Utilities | — | Individual productivity tool |
| Print server / fleet management | End-User Computing > Printing & Scanning SW | IT Ops > (visibility) | End-user function; ops has fleet interest |

---

## Scope Boundaries & Future Considerations

### In Scope
- All enterprise software (any delivery model: on-prem, SaaS, hybrid, open source)
- Compute-related hardware: servers, storage, networking, endpoints, collaboration devices, security appliances
- Cloud services classified by what they do (IaaS → IT Ops, SaaS → by function)

### Out of Scope (for now)
- **IoT & Embedded Systems** — Sensors, PLCs, microcontrollers, industrial IoT gateways. These are compute-adjacent but represent a distinct operational domain. Candidate for a future 11th governance group if demand warrants.
- **Operational Technology (OT)** — SCADA systems, industrial control systems, manufacturing automation. Distinct governance and safety requirements.
- **Physical security** (not IT-integrated) — Cameras, alarms, access control that don't integrate with IT identity systems.
- **Telecom carrier infrastructure** — Carrier-grade equipment, cell towers, PSTN infrastructure.
- **Consumer electronics** — Personal devices not managed or deployed by the enterprise.

### Future Considerations
- **AI Governance** — As AI tools proliferate across every category (AI coding assistants in App Dev, AI analytics in Data, AI security in Security), organizations may need a cross-cutting AI governance overlay or a dedicated 11th group. For now, AI products are classified by their primary function within existing groups.
- **Sustainability / Green IT** — Energy monitoring, carbon tracking, and sustainability reporting for IT assets may emerge as a governance concern.

---

## Taxonomy Statistics (v0.2)

- **Level 1 branches:** 2 (Software, Computing Hardware)
- **Level 2 governance groups:** 10
- **Level 3 categories (Software):** ~85
- **Level 3 categories (Hardware):** ~30
- **Level 4+ subcategories:** ~95
- **Total nodes:** ~220+

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v0.1 | 2026-02-05 | Initial draft based on G2, TOGAF, ArchiMate, and other reference sources. 9 governance groups. |
| v0.2 | 2026-02-05 | Added multi-category classification. Split Business Applications into Business Operations + Customer & Revenue Technology. Added communications APIs, content management, media production, e-commerce, UX design, AI-assisted development. Resolved DevOps/IaC boundary. Added telephony hardware. Expanded edge cases table. Documented scope boundaries. |

---

## Key Design Decisions Log

| Decision | Rationale |
|----------|-----------|
| HW and SW always separate at L1 | Governance teams may differ; hardware lifecycle and standards processes differ fundamentally from software |
| Security is its own group | Security products have distinct compliance, audit, and risk governance needs regardless of what layer they protect |
| Classify by capability, not delivery model | SaaS vs on-prem is a deployment detail, not a functional classification |
| DevOps/IaC primary home is IT Ops, secondary App Dev | The *purpose* is infrastructure management; the *users* are developers. Governance follows purpose. |
| Content management under Customer & Revenue | Enterprise CMS is primarily customer-facing content publishing, governed by marketing/digital teams |
| Media production under Engineering & Design | Creative tools share governance patterns with CAD/design tools (specialized licenses, workstation requirements, creative team ownership) |
| Telephony hardware under Collaboration | VoIP/PBX serves communication function, governed alongside other communication infrastructure |
| Network firewalls under Security (not Networking) | Security team owns all security-purposed devices; networking has secondary visibility |
| Multi-category max 2 secondaries | Prevents scope creep; if more than 2 are needed, the taxonomy likely needs structural adjustment |
