# Delivery plan

The work is split into four developer-friendly phases. Each screen and feature folder should remain small, with shared UI kept separate from business logic.

## Phase 1 — Foundation and product experience

**Complete.** Brand and repository setup, landing page, sign-in, three-step account and organization onboarding, workspace creation, protected dashboard shell, FastAPI service, JWT auth with rotating refresh sessions, PostgreSQL models and Alembic migration, Docker Compose, and run instructions. Dashboard counts, vendor trust snapshot, pending approvals and recent activity use tenant-scoped API records.

## Phase 2 — Trust and organization

**Complete.** Organization members, tenant roles and permissions, departments, one-time invitation links, vendor management, verification lifecycle, certifications and Trust Passport.

## Phase 3 — Procurement workflows

**Complete.** RFQ creation and approval to publish, side-by-side bid comparison, award/decline, approval queue, contract review and activation, and purchase orders with line items and approval.

## Phase 4 — Operations and verification

**Complete as a self-contained workspace implementation.** Tenant-scoped shipment, finance/invoice, risk, credential-reference and asset registers; workflow status actions; local rules-based Trust Assistant; and a SHA-256 linked proof ledger with authenticated verification endpoint. The proof ledger is a practical local alternative to a public blockchain. Shipment records expose tracking references and delivery milestones; external carrier feeds, payment rails, public blockchain anchoring, uploaded credential vaults, hosted AI/RAG and external CI/observability integrations require service credentials and remain integration points.

Phase 4 adds `0003_operations` and the `/operations` API group. Screens are separate routes: `/shipments`, `/finance`, `/risks`, `/credentials`, `/assets`, `/proofs` and `/assistant`.

## Parallel ownership guide

1. Product shell and navigation
2. Brand and design system
3. Auth and onboarding screens
4. Dashboard and reporting widgets
5. Organization and RBAC API
6. Vendor and trust features
7. Procurement workflows
8. Quality, integration and delivery

Owners can work in separate route/feature folders and agree on shared contracts before integration.
