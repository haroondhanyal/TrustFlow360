<p align="center"><img src="apps/web/public/trustflow360-logo.svg" width="360" alt="TrustFlow 360" /></p>

<h1 align="center">TrustFlow 360</h1>
<p align="center"><strong>Trust every transaction. Verify every relationship.</strong></p>

TrustFlow 360 is an enterprise trust, procurement, supply chain and verification platform. This repository is being built in four practical phases, with small, focused screens and reusable components so multiple developers can work in parallel.

## Project phases

1. **Foundation and product experience** — monorepo, brand, design tokens, landing, sign-in, account and organization onboarding, dashboard, API, auth and PostgreSQL.
2. **Trust and organization** — users, roles, departments, vendor management and Trust Passport.
3. **Procurement workflows** — RFQs, bids, approvals, contracts and purchase orders.
4. **Operations and verification** — shipments, QR verification, finance, risk, credentials, assets, blockchain and AI foundations.

Each phase is delivered incrementally. The product brief's wider modules are grouped into these four delivery phases.

## Phase 1 structure

```text
apps/web/       Next.js App Router application
  app/          One route per screen (home, login, signup, dashboard)
  components/   Shared UI and brand components
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

This starts PostgreSQL, applies the initial Alembic migration, starts the API at <http://localhost:8000> and web app at <http://localhost:3000>. API docs are at <http://localhost:8000/docs>. The PostgreSQL volume persists between runs; `npm run stack:down` stops the services without deleting data.

Available screens: `/`, `/login`, `/signup`, and `/dashboard`. Sign-up creates the account, organization and named workspace. The dashboard route requires an auth cookie.

## Tech choices

- Next.js App Router, React and TypeScript
- CSS variables and small, reusable React components
- FastAPI, SQLAlchemy, PostgreSQL and Alembic for the account, organization and refresh-session foundation.
- Argon2 password hashes, short-lived JWT access tokens, rotating refresh sessions and same-site `HttpOnly` browser cookies.
- Dashboard metrics and activity use a separate realistic demo-data module until the Phase 2 business APIs are delivered.

## Configuration and security

Docker Compose uses development-only credentials. Before deploying, provide a strong `JWT_SECRET` through the environment or secret manager, set `APP_ENV=production`, and configure the allowed `CORS_ORIGINS`. Never use the local Compose password or development JWT secret in a deployed environment.

## Developer workflow

Keep each screen in its own route folder, move shared visual elements into `components/`, API schemas into `apps/api/app/schemas.py`, and demo content into `apps/web/lib/`. Avoid giant page files and keep feature modules independently assignable across the eight developers.

## Screenshots

Screenshots will be added as the screens are reviewed in a running environment.

## Roadmap

See [docs/architecture/phase-plan.md](docs/architecture/phase-plan.md) for phase boundaries and parallel work areas.
