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

The seeder creates 20 role-based development accounts and 25–30 records for each data workspace. See [DATA-README.md](DATA-README.md) for all sign-in credentials, record counts and reset steps. Passwords in that file are intentionally limited to local demo use.

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

The screenshots below were captured from the running app with the seeded demo workspace. The authenticated workspace screens show real API-backed sample data, including 30-row tables. Expand a section to view its screens; each image links to its full-size PNG. For a compact index, see the [screenshot gallery](docs/screenshots/README.md). Demo account details and sample data counts are in [DATA-README.md](DATA-README.md).

### Public and account screens

<details>
<summary>Landing page and account flows (4 screens)</summary>

#### Landing page
<a href="docs/screenshots/01-home.png"><img src="docs/screenshots/01-home.png" alt="TrustFlow 360 landing page" width="100%"></a>

#### Sign in
<a href="docs/screenshots/02-login.png"><img src="docs/screenshots/02-login.png" alt="TrustFlow 360 sign in screen" width="100%"></a>

#### Sign up
<a href="docs/screenshots/03-signup.png"><img src="docs/screenshots/03-signup.png" alt="TrustFlow 360 sign up screen" width="100%"></a>

#### Accept invitation
<a href="docs/screenshots/04-invitation-join.png"><img src="docs/screenshots/04-invitation-join.png" alt="TrustFlow 360 invitation acceptance screen" width="100%"></a>

</details>

### Organization and procurement

<details>
<summary>Organization, vendors, sourcing, and purchasing (9 screens)</summary>

#### Dashboard
<a href="docs/screenshots/05-dashboard.png"><img src="docs/screenshots/05-dashboard.png" alt="TrustFlow 360 dashboard with seeded workspace data" width="100%"></a>

#### People, departments, and roles
<a href="docs/screenshots/06-organization.png"><img src="docs/screenshots/06-organization.png" alt="Organization members, departments, roles, and invitations" width="100%"></a>

#### Vendors
<a href="docs/screenshots/07-vendors.png"><img src="docs/screenshots/07-vendors.png" alt="Vendor management with 30 seeded records" width="100%"></a>

#### Vendor Trust Passport
<a href="docs/screenshots/08-vendor-passport.png"><img src="docs/screenshots/08-vendor-passport.png" alt="Vendor Trust Passport" width="100%"></a>

#### RFQs
<a href="docs/screenshots/09-rfqs.png"><img src="docs/screenshots/09-rfqs.png" alt="RFQ management with 30 seeded records" width="100%"></a>

#### Bid comparison
<a href="docs/screenshots/10-bids.png"><img src="docs/screenshots/10-bids.png" alt="Bid comparison workspace" width="100%"></a>

#### Approvals
<a href="docs/screenshots/11-approvals.png"><img src="docs/screenshots/11-approvals.png" alt="Approval queue" width="100%"></a>

#### Contracts
<a href="docs/screenshots/12-contracts.png"><img src="docs/screenshots/12-contracts.png" alt="Contract management" width="100%"></a>

#### Purchase orders
<a href="docs/screenshots/13-purchase-orders.png"><img src="docs/screenshots/13-purchase-orders.png" alt="Purchase order management" width="100%"></a>

</details>

### Operations and verification

<details>
<summary>Logistics, finance, risk, assets, and proof verification (8 screens)</summary>

#### Shipments
<a href="docs/screenshots/14-shipments.png"><img src="docs/screenshots/14-shipments.png" alt="Shipment tracking workspace" width="100%"></a>

#### Finance and invoices
<a href="docs/screenshots/15-finance.png"><img src="docs/screenshots/15-finance.png" alt="Finance and invoice workspace" width="100%"></a>

#### Risks and compliance
<a href="docs/screenshots/16-risks.png"><img src="docs/screenshots/16-risks.png" alt="Risk and compliance workspace" width="100%"></a>

#### Credentials
<a href="docs/screenshots/17-credentials.png"><img src="docs/screenshots/17-credentials.png" alt="Credential registry" width="100%"></a>

#### Assets
<a href="docs/screenshots/18-assets.png"><img src="docs/screenshots/18-assets.png" alt="Asset register" width="100%"></a>

#### Proof ledger
<a href="docs/screenshots/19-proof-ledger.png"><img src="docs/screenshots/19-proof-ledger.png" alt="Hash-linked proof ledger" width="100%"></a>

#### Proof verification
<a href="docs/screenshots/20-proof-verification.png"><img src="docs/screenshots/20-proof-verification.png" alt="Public proof verification screen" width="100%"></a>

#### Trust Assistant
<a href="docs/screenshots/21-trust-assistant.png"><img src="docs/screenshots/21-trust-assistant.png" alt="Trust Assistant screen" width="100%"></a>

</details>

## Roadmap

See [docs/architecture/phase-plan.md](docs/architecture/phase-plan.md) for phase boundaries and parallel work areas.
