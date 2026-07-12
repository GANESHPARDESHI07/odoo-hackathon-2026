# 10 — DEVELOPER 4 · FINANCE, DASHBOARD & ANALYTICS

> Paste below the line into Claude Code, or say: *"Read docs/00, docs/02 §5–6, docs/05 §5–6 and docs/10_DEVELOPER_4.md, then follow 10."*

---

## ROLE
You are Developer 4 on a 4-person, 8-hour Odoo hackathon team building TransitOps. You own **Finance & Insight**: fuel logs, expenses, the KPI dashboard, reporting views, and the demo seed data. Your work is what judges see first (dashboard) and last (analytics) — you own the wow factor and the numbers being *right*.

## READ FIRST
`docs/00_PROJECT_CONTRACT.md`, `docs/02_DATABASE_CONTRACT.md` §5–6, `docs/05_UI_CONTRACT.md` §5–6 (your KPI definitions are LOCKED there), `docs/16_CONTRACTS.md` (E-10).

## OWNERSHIP
- **You may edit ONLY:** `models/fuel_log.py`, `models/expense.py`, `views/fuel_expense_views.xml`, `views/dashboard_views.xml`, `static/src/dashboard/*`, `demo/demo_data.xml`, `report/*` (stretch).
- **You must NEVER edit:** manifest (your asset glob + demo entry are already registered), `__init__` files, security files, menus.xml, vehicle/driver/trip/maintenance files. Requests → `REQUEST TO <owner>: ...`.

## SCOPE

**Sprint 1 (0:30–2:15).** Acceptance: fuel/expense CRUD; dashboard stub renders live counts.
1. Flesh out `transitops.fuel.log` per `02` §5 (constraint E-10, `source` selection) and `transitops.expense` per §6.
2. Views + leaf menus per `05` §1/§4: `menu_transitops_fuel_log`, `menu_transitops_expense` under Finance.
3. Upgrade the skeleton dashboard stub (already rendering from Hour 0) to the full 8-card grid per `05` §5 — exact KPI domains, utilization math (1dp, guard empty fleet), clean SCSS cards.
4. **Demo seed data v1** in `demo/demo_data.xml`: 4 demo users (fm@transitops.demo, dispatch@…, safety@…, analyst@…, password `transitops`, each in exactly one group; admin gets all four groups) + 5 vehicles (statuses: 3 available, 1 in_shop **with matching open maintenance record**, 1 retired) + 4 drivers (2 valid-available, 1 with **expired license "Ravi Kumar"**, 1 suspended). Do NOT create "Van-05" or "Alex" — the demo creates those live.

**Sprint 2 (2:45–4:45).**
5. Card click-through: each KPI card `doAction`s to the matching filtered list view.
6. Dashboard filters: Vehicle Type + Region `<select>`s re-running the vehicle-based counts (spec §3.2). Caption noting trip/driver cards are fleet-wide.
7. Seed data v2 (needs D3's actions merged): 3 completed trips with revenue/distances + matching fuel logs + 2 expenses + 1 draft trip — so efficiency, op-cost and ROI are non-zero. Create completed trips **through the actions** if XML state-writing fights you: a tiny `<function>` call or note in `11` — simplest reliable route: create records in XML with explicit state + odometer fields (allowed in demo data since it bypasses buttons legitimately), and verify vehicle computes pick them up.
8. Reporting per `05` §6: trip pivot/graph action + the Vehicle Costs & ROI list (the CSV-export surface). Leaf menus under Reporting.

**Sprint 3 (5:15–6:15).**
9. Dashboard polish: number formatting, utilization emphasis, subtle refresh on filter change; verify every card's count against seed data by hand (QA will).
10. STRETCH only if green: one QWeb PDF "Vehicle Cost Card" (name, reg, totals, efficiency, ROI) — report action on vehicle. If it fights you >30 min, drop it; the bonus isn't worth demo risk.

## CONTRACTS YOU EXPOSE (frozen)
fuel.log creation field names (D3 auto-creates them — see `03` fuel.log card; if you rename anything, trips break); E-10 text; KPI definitions (QA asserts the math).

## CONTRACTS YOU CONSUME (read-only)
vehicle `status/vehicle_type/region` + all financial computes (D1 computes them — you only display); driver `status`; trip `state/actual_distance_km/revenue/dispatch_datetime`. Group XML IDs for demo users.

## IMPLEMENTATION NOTES / GOTCHAS
- OWL: `useService("orm")` → `searchCount(model, domain)`; `useService("action")` for click-through; template in `static/src/dashboard/dashboard.xml`, component registered `registry.category("actions").add("transitops.dashboard", …)` — the stub already wires all this; extend, don't rewrite.
- JS/SCSS/XML asset changes: hard-refresh browser (Ctrl+Shift+R); template changes may need `-u transitops`. Python change → restart server.
- Demo users in XML: set `login`, `name`, `password`, `groups_id` with `[(6,0,[ref(...)])]` including `base.group_user`.
- Keep everything framework-native: no chart.js, no external fonts. Pivot/graph views ARE the "charts" deliverable.
- If OWL misbehaves near a checkpoint, invoke the fallback in `21` §6 immediately — a filtered kanban beats a broken dashboard.

## WORKFLOW LOOP / SELF-QA / GIT
Standard loop; branch `feat/d4-finance` only; commits like `feat(dashboard): KPI cards + click-through`.
Self-QA slice: upgrade clean on a FRESH db **with demo data** (`-i transitops` on new db) · negative liters blocked (E-10) · every KPI card equals a hand count of seed data · utilization math correct · card clicks open correctly-filtered lists · filters narrow vehicle cards only · pivot shows distance/revenue by vehicle/month · Vehicle Costs list exports to CSV (do the export once yourself) · demo users log in with correct role visibility.

## STATUS OUTPUT / ESCALATION
`docs/17` at checkpoints. Seed-data needs from other models (e.g., a field default fighting XML) → `REQUEST TO <owner>`. Blocked >10 min → surface.
