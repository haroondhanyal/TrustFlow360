<p align="center"><img src="apps/web/public/trustflow360-logo.svg" width="360" alt="TrustFlow 360" /></p>

<h1 align="center">TrustFlow 360</h1>
<p align="center"><strong>Trust every transaction. Verify every relationship.</strong></p>

TrustFlow 360 is an enterprise trust, procurement, supply chain and verification platform. This repository is being built in four practical phases, with small, focused screens and reusable components so multiple developers can work in parallel.

## Project phases

1. **Foundation and product experience** — monorepo, brand, design tokens, landing, sign-in, onboarding shell and dashboard.
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
apps/api/       Reserved for the FastAPI service in the next foundation increment
docs/           Architecture and developer notes
```

## Run the web app

Requirements: Node.js 20.9+ and npm.

```bash
cd apps/web
npm install
npm run dev
```

Open <http://localhost:3000>. Available screens: `/`, `/login`, `/signup`, and `/dashboard`.

## Tech choices

- Next.js App Router, React and TypeScript
- CSS variables and small, reusable React components
- FastAPI, PostgreSQL and Alembic are planned for the API/data layer; no live API or database is wired in this UI-only Phase 1 starter yet.

## Developer workflow

Keep each screen in its own route folder, move shared visual elements into `components/`, and keep demo content in `lib/`. Avoid giant page files and keep feature modules independently assignable across the eight developers.

## Screenshots

Screenshots will be added as the screens are reviewed in a running environment.

## Roadmap

See [docs/architecture/phase-plan.md](docs/architecture/phase-plan.md) for phase boundaries and parallel work areas.
