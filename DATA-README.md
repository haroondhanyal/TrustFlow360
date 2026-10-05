# TrustFlow 360 demo data and accounts

This file documents credentials and sample records created by `npm run seed:demo`. These are **development-only demo accounts** for the local NexaTel workspace (`nexatel-demo`). They are not production accounts. Do not reuse these passwords outside this demo environment.

## Demo sign-in accounts

All accounts use the same local workspace. The `organization_admin` account can manage all seeded screens. Other accounts demonstrate the listed role permissions.

| # | Email | Role | Password |
|---:|---|---|---|
| 1 | `admin@example.com` | Organization admin | `Demo-TrustFlow-123!` |
| 2 | `buyer01@example.com` | Procurement manager | `TF360-Buyer01-2026!` |
| 3 | `buyer02@example.com` | Procurement manager | `TF360-Buyer02-2026!` |
| 4 | `buyer03@example.com` | Procurement manager | `TF360-Buyer03-2026!` |
| 5 | `vendor01@example.com` | Vendor manager | `TF360-Vendor01-2026!` |
| 6 | `vendor02@example.com` | Vendor manager | `TF360-Vendor02-2026!` |
| 7 | `vendor03@example.com` | Vendor manager | `TF360-Vendor03-2026!` |
| 8 | `finance01@example.com` | Finance manager | `TF360-Finance01-2026!` |
| 9 | `finance02@example.com` | Finance manager | `TF360-Finance02-2026!` |
| 10 | `finance03@example.com` | Finance manager | `TF360-Finance03-2026!` |
| 11 | `audit01@example.com` | Auditor | `TF360-Audit01-2026!` |
| 12 | `audit02@example.com` | Auditor | `TF360-Audit02-2026!` |
| 13 | `audit03@example.com` | Auditor | `TF360-Audit03-2026!` |
| 14 | `member01@example.com` | Viewer | `TF360-Member01-2026!` |
| 15 | `member02@example.com` | Viewer | `TF360-Member02-2026!` |
| 16 | `member03@example.com` | Viewer | `TF360-Member03-2026!` |
| 17 | `member04@example.com` | Viewer | `TF360-Member04-2026!` |
| 18 | `member05@example.com` | Viewer | `TF360-Member05-2026!` |
| 19 | `member06@example.com` | Viewer | `TF360-Member06-2026!` |
| 20 | `member07@example.com` | Viewer | `TF360-Member07-2026!` |

## Seeded record counts

The seed is additive and idempotent: running it again fills missing demo records without duplicating the numbered sample rows.

| Workspace area | Seeded data |
|---|---:|
| Organization members | 20 accounts |
| Departments | 25 |
| Roles | 6 built-in + 24 custom |
| Invitations | 25 historical demo invitations |
| Vendors | 30 |
| Vendor certifications | At least 30 |
| RFQs | 30, with line items and specifications |
| Bids | 30 |
| Approvals | 30 |
| Contracts | 30 |
| Purchase orders and lines | 30 each |
| Shipments | 30 |
| Finance / invoices | 30 |
| Risk records | 30 |
| Credentials | 30 |
| Assets | 30 |
| Verification proofs | 30 |

Sign-in, signup, invitation acceptance and the Trust Assistant are interactive flows rather than data tables; the seed provides accounts/links/records for those screens to use.

Profile photos are optional and can be added, changed or removed on `/profile`. The example photo shown in the screenshots was uploaded to the local development admin account; a newly seeded database starts with initials until a user adds a photo.

## Reset and seed

To add missing demo rows to the current local database:

```bash
npm run seed:demo
```

To reset **all** local data, stop the stack and remove its database volume, then start and seed again:

```bash
npm run stack:down
docker compose down --volumes
npm run stack:up
npm run seed:demo
```

Removing the Compose volume permanently deletes the local database. The normal seed command does not delete or overwrite user-entered records.
