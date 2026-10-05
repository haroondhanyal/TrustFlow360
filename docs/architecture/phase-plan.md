# Delivery plan

The work is split into four developer-friendly phases. Each screen and feature folder should remain small, with shared UI kept separate from business logic.

## Phase 1 — Foundation and product experience

**Complete.** Brand and repository setup, landing page, sign-in, three-step account and organization onboarding, workspace creation, protected dashboard shell, FastAPI service, JWT auth, PostgreSQL models and Alembic migration, Docker Compose, and run instructions. Dashboard summary cards use isolated demo data; Phase 2 and 3 screens use tenant-scoped API records.

## Phase 2 — Trust and organization

**Complete.** Organization members, tenant roles and permissions, departments, one-time invitation links, vendor management, verification lifecycle, certifications and Trust Passport.

## Phase 3 — Procurement workflows

**Complete.** RFQ creation and approval to publish, side-by-side bid comparison, award/decline, approval queue, contract review and activation, and purchase orders with line items and approval.

## Phase 4 — Operations and verification

Shipments and QR verification, finance and risk, credentials and assets, blockchain proofs, AI/RAG, hardening, CI and observability.

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
