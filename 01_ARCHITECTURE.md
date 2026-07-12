# 01 — ARCHITECTURE

## 1. System Overview

TransitOps is a single Odoo 18 Community addon (`transitops`) running on standard Odoo infrastructure: PostgreSQL for persistence, the Odoo ORM for business logic and access control, standard backend web client (list/form/kanban/graph/pivot views) for 95% of the UI, plus one custom OWL client action for the KPI dashboard. Authentication, sessions, RBAC plumbing, CSV export, responsive layout, audit trail (chatter) and attachments are inherited from the framework — we build **only the domain layer** and spend saved time on business rules and demo polish.

```
Browser (Odoo web client, responsive)
 ├── Standard views: list / form / search / kanban / graph / pivot
 └── OWL Dashboard (client action, ORM RPC → search_count/read_group)
            │
Odoo Server (transitops addon)
 ├── Models: vehicle, driver, trip, maintenance, fuel.log, expense
 ├── Business rules: constraints + action_* methods (FSMs)
 ├── Security: 4 groups + ACL CSV
 └── mail.thread: tracking, chatter, attachments
            │
PostgreSQL (one table per model; FK = many2one)
```

## 2. Module Boundaries (logical, inside one addon)

| Bounded context | Models | Views | Owner |
|---|---|---|---|
| **Fleet Core** | vehicle, maintenance | vehicle_views, maintenance_views | Dev 1 (Lead) |
| **People & Access** | driver, security groups/rules | driver_views, record_rules | Dev 2 |
| **Operations** | trip (the orchestrator) | trip_views | Dev 3 |
| **Finance & Insight** | fuel.log, expense, dashboard, reports, demo data | fuel_expense_views, dashboard_views, static/src | Dev 4 |

Boundaries are enforced socially (file ownership, §3 of `00`) and technically (cross-context interaction only through the interfaces in `03`/`04`/`06`).

## 3. Dependency Graph

```
            ┌──────────────┐
            │    trip (D3) │  writes status of ↓, reads fields of ↓
            └──────┬───────┘
        ┌──────────┴──────────┐
        ▼                     ▼
  vehicle (D1) ◄──────── maintenance (D1)   (maintenance writes vehicle.status)
        ▲                     
        │ vehicle_id FKs      
   ┌────┴─────┐               
fuel.log (D4)  expense (D4)   (pure children: read/aggregate only)
        
driver (D2) ◄── trip (D3 writes driver.status, reads license fields)

vehicle computed financials (D1) ← depend on → fuel.log, maintenance, trip (completed)
dashboard (D4) ← read-only search_count over vehicle, driver, trip
```

Key property: **only Trip and Maintenance mutate anything outside themselves**, and only the two documented fields (`vehicle.status`, `driver.status`). Everything else is read/aggregate. This is why parallel work is safe.

## 4. Data Flow (happy path)

1. FM registers Vehicle (`available`) → SO registers Driver (`available`).
2. DP creates Trip `draft` (UI already filters to available vehicle/driver, valid license — BR-02/03/04).
3. `action_dispatch` re-validates everything server-side, snapshots `start_odometer_km` from the vehicle, stamps `dispatch_datetime`, flips vehicle+driver → `on_trip` (BR-06).
4. `action_complete` requires `end_odometer_km ≥ start` (BR-11), writes odometer back to vehicle, flips both → `available` (BR-07), auto-creates a fuel log if `fuel_consumed_l > 0`.
5. Fuel/maintenance/expense records aggregate into vehicle stored computes (BR-14/15) → dashboard KPIs and Reporting pivots update immediately.
6. FM opens Maintenance → vehicle `in_shop`, vanishes from dispatch pool (BR-09); closing restores `available` (BR-10).

## 5. Business Flow — State Machines

```
VEHICLE  available ──dispatch──▶ on_trip ──complete/cancel──▶ available
         available ──maint open─▶ in_shop ──maint close──▶ available
         available|in_shop ──action_retire──▶ retired (terminal; blocked while on_trip)

DRIVER   available ⇄ on_trip (via trip actions only)
         available ⇄ off_duty (manual buttons, D2)
         available|off_duty ──suspend──▶ suspended ──reinstate──▶ available
         (suspend blocked while on_trip)

TRIP     draft ──dispatch──▶ dispatched ──complete──▶ completed
         draft ──cancel──▶ cancelled
         dispatched ──cancel──▶ cancelled (restores resources)

MAINT    open ──close──▶ done        open ──cancel──▶ cancelled
```

## 6. Why This Architecture Wins the Judging

- **Merge safety:** frozen shared files + one-owner-per-file + contracts = merges are `git merge` with near-zero conflicts.
- **Speed:** ~80% of mandatory deliverables (auth, RBAC plumbing, CRUD UI, export, responsive, filters, charts) come from the framework; the team's 8 hours go into the 20% judges actually score — business rules and flow automation.
- **Reliability:** every rule enforced twice — UI domain (good UX) **and** Python constraint/action (integrity). Concurrency-safe: `action_dispatch` re-reads live statuses, so two dispatchers racing for one vehicle can't double-book.
- **Demo quality:** state changes are visible (status badges, statusbar, chatter tracking lines) — every business rule is a screen moment.
- **Claude Code friendliness:** small files, one model per file, explicit contracts to point Claude at, no cross-file surprises.

## 7. Deliberate Non-Goals (do not build)

Custom REST controllers, websockets/live GPS, multi-company, portal access, chart.js/external JS libs, custom auth, Docker orchestration mid-hackathon, i18n beyond `_()` wrappers, record-level ownership rules (unless Sprint-3 green). Every one of these is a time sink with zero judging payoff for this spec.
