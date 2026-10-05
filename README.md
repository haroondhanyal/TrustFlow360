<p align="center"><img src="apps/web/public/trustflow360-logo.svg" width="360" alt="TrustFlow 360" /></p>

<h1 align="center">TrustFlow 360</h1>
<p align="center"><strong>Trust every transaction. Verify every relationship.</strong></p>

TrustFlow 360 is an enterprise trust, procurement, supply chain and verification platform. This repository is being built in four practical phases, with small, focused screens and reusable components so multiple developers can work in parallel.

## Project phases

1. **Foundation and product experience** — monorepo, brand, design tokens, landing, sign-in, account and organization onboarding, dashboard, API, auth and PostgreSQL.
2. **Trust and organization** — users, roles, departments, vendor management and Trust Passport.
3. **Procurement workflows** — RFQs, bids, approvals, contracts and purchase orders.
4. **Operations and verification** — shipments, proof verification links, finance, risk, credentials, assets, blockchain and AI foundations.

All four phases are implemented. Phase 4 provides tenant-scoped operations screens and API workflows with self-hosted alternatives for external integrations.

## Phase 1 structure

```text
apps/web/       Next.js App Router application
  app/          One route per screen (home, login, signup, dashboard)
  components/   Brand, authentication and reusable module screens
  lib/          Demo dashboard data and shared helpers
  public/       Logo and static assets
apps/api/       FastAPI service, authentication, organization API and migrations
docs/           Architecture and developer notes
```

## Run the web app

Requirements: Node.js 20.9+ and npm for the web app, or Docker Compose for the complete stack.

```bash
cd apps/web
npm install
npm run dev
```

The standalone web command is useful for working on screens; account creation and sign-in need the API. For the complete app with PostgreSQL and FastAPI, run this from the repository root:

```bash
npm run stack:up
```

If port `3000` is already in use, start the web app on port `3001` with `WEB_PORT=3001 npm run stack:up -- --detach` and open <http://localhost:3001>.

This starts PostgreSQL, applies the initial Alembic migration, starts the API at <http://localhost:8000> and web app at <http://localhost:3000>. API docs are at <http://localhost:8000/docs>. The PostgreSQL volume persists between runs; `npm run stack:down` stops the services without deleting data.

To populate a local demo workspace, run `npm run seed:demo` after the stack is ready. Demo sign-in: `admin@example.com` / `Demo-TrustFlow-123!` (development only). Change or remove this account before sharing a non-local deployment.

Available screens include `/`, `/login`, `/signup`, `/dashboard`, the organization and procurement workspaces, plus `/shipments`, `/finance`, `/risks`, `/credentials`, `/assets`, `/proofs` and `/assistant`. Sign-up creates the account, organization and named workspace. Workspace screens require an authenticated session.

## Tech choices

- Next.js App Router, React and TypeScript
- CSS variables and small, reusable React components
- FastAPI, SQLAlchemy, PostgreSQL and Alembic for the account, organization and refresh-session foundation.
- Argon2 password hashes, short-lived JWT access tokens, rotating refresh sessions and same-site `HttpOnly` browser cookies.
- Dashboard counts, vendor trust snapshot, pending approvals and recent activity load from the signed-in organization’s API records.
- Protected workspace navigation renews short-lived access tokens with the rotating refresh session.
- Phase 2: tenant-scoped users, custom roles/permissions, departments, copyable one-time team invitations, vendor lifecycle, certificates, verification and Trust Passport.
- Phase 3: RFQ creation and approval to publish, comparable vendor bids with best-price/technical/delivery highlights, award/decline, contract review, purchase orders with line items, and approval decisions.
- Phase 4: shipment tracking, invoice and payment status, risk reviews, credential references, asset register, local Trust Assistant summaries, and SHA-256 linked proofs with organization-scoped verification.

## Phase 4 alternatives and integration points

Phase 4 works in the self-hosted stack without paid third-party services. Carrier updates are recorded manually against shipments; finance tracks invoice and payment state but does not initiate transfers; credentials are references and do not store uploaded documents; the Trust Assistant uses local workspace rules rather than an external language model; and proofs form an organization-scoped SHA-256 chain. The proofs are tamper-evident application data, not transactions anchored to a public blockchain. Carrier, storage, payment, hosted AI and blockchain providers can be connected later through API adapters.

## Configuration and security

Docker Compose uses development-only credentials. Before deploying, provide a strong `JWT_SECRET` through the environment or secret manager, set `APP_ENV=production`, and configure the allowed `CORS_ORIGINS`. Never use the local Compose password or development JWT secret in a deployed environment.

## Developer workflow

Keep each screen in its own route folder, move shared visual elements into `components/`, API schemas into `apps/api/app/schemas.py`, and demo content into `apps/web/lib/`. Avoid giant page files and keep feature modules independently assignable across the eight developers.

### Phase 2 and 3 API groups

- `GET/POST /vendors`, `PATCH /vendors/{id}`, verify/suspend actions, certifications and `/vendors/{id}/passport`
- `/organization/users`, `/organization/roles`, `/organization/departments`, `/organization/invitations` and `/organization/invitations/accept`
- `GET/POST /rfqs`, publish approval, bid submission/comparison/award, `/approvals`, `/contracts` and `/purchase-orders` with items
- `/operations/shipments`, `/operations/finance`, `/operations/risks`, `/operations/credentials`, `/operations/assets`, `/operations/proofs`, `/operations/verify/{digest}` and `/operations/assistant`
- All business records carry an `organization_id`; API lookups check the signed-in user's tenant before returning or changing a record.

## Screenshots

Screenshots will be added as the screens are reviewed in a running environment.

## Roadmap

See [docs/architecture/phase-plan.md](docs/architecture/phase-plan.md) for phase boundaries and parallel work areas.
