# Delivery plan

The work is split into four developer-friendly phases. Each screen and feature folder should remain small, with shared UI kept separate from business logic.

## Phase 1 — Foundation and product experience

**Complete.** Brand and repository setup, landing page, sign-in, three-step account and organization onboarding, workspace creation, protected dashboard shell, FastAPI service, JWT auth, PostgreSQL models and Alembic migration, Docker Compose, and run instructions. Dashboard cards use isolated demo data until the Phase 2 business APIs are added.

## Phase 2 — Trust and organization

Organization members, roles, departments, vendor lifecycle, verification status and Trust Passport.

## Phase 3 — Procurement workflows

RFQ creation and publishing, bid submission and comparison, approvals, contracts and purchase orders.

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
