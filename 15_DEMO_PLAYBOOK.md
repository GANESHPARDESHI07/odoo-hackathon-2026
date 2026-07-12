# 15 — DEMO PLAYBOOK (6 minutes, judge-facing)

**Pre-demo reset checklist (2 min before):** final `transitops_demo` db · logged out · browser zoom 100%, bookmarks bar hidden, notifications off · second tab pre-opened on Vehicles list (for the status-flip reveal) · seed data intact: no leftover "Van-05"/"Alex" from rehearsal (delete draft-state leftovers; rehearse on copies) · this script printed/second screen. Presenter drives, one teammate narrates numbers, backup presenter ready.

Timings assume 6:00 total. If judges interrupt, answer briefly and resume — the script has slack in §7.

## 0:00 · Login — "secure by default"
Show the login page, log in as `fm@transitops.demo`.
> "TransitOps replaces the spreadsheets and logbooks logistics teams still run on. Everything you'll see sits behind session-based authentication with four business roles — Fleet Manager, Dispatcher, Safety Officer, Analyst — enforced at the ORM level, not just hidden menus."

## 0:30 · Dashboard — "operational visibility"
> "One screen answers the fleet's morning questions: total fleet, available, in maintenance, on trip, active and pending trips, drivers on duty, and live utilization." Click one card → filtered list → back. Touch the Type/Region filter once. "Every number is a live query — watch it move in a minute."

## 1:15 · Vehicle + Driver registration (spec steps 1–2)
Fleet → Vehicles → New: **Van-05**, van, capacity **500 kg**, odometer 12000, acquisition ₹4,00,000 → save (point at the Available badge). Drivers → New: **Alex**, valid license, expiry next year → save.
> "Registration numbers are unique at the database level, and notice the chatter — every status change is audit-trailed for free, and documents can be attached right here." *(that's the document-management bonus, claimed in one sentence)*

## 2:00 · Trip creation + THE overweight block (steps 3–4 + negative demo #1)
Operations → Trips → New: source/destination, pick Van-05 + Alex, cargo **600** kg → Save → **error appears**.
> "Business rules aren't warnings here — *'Cargo weight 600 kg exceeds capacity of Van-05, 500 kg'* — the ORM refuses the record." Change to **450** → saves, sequence number TRIP/2026/… appears.

## 2:45 · Dispatch — automatic status choreography (step 5)
Hit **Dispatch**. Flip to the pre-opened Vehicles tab → Van-05 is **On Trip**; show Alex likewise; flash the dashboard: Available −1, Active Trips +1, utilization up.
> "One click re-validated vehicle, driver and license server-side, snapshotted the odometer, and flipped both resources — no double-booking is possible: try creating another trip…" open New Trip, drop the vehicle list down: **Van-05 is gone**. "…and even a stale form gets rejected by the same server check. Two dispatchers racing for one van — the second one loses safely."

## 3:45 · Negative demo #2 — compliance
Still in the driver dropdown: point out **Ravi Kumar** (expired license) and the suspended driver are absent.
> "Expired licenses and suspended drivers never reach a trip — the Safety Officer's world is enforced automatically." (If asked, show Drivers → License Expired filter.)

## 4:15 · Complete the trip (steps 6–7)
Open the trip → end odometer **12150**, fuel **15 L / ₹1,500** → **Complete**.
> "Both resources are Available again, the vehicle's odometer advanced to 12150, and — Finance → Fuel Logs — a fuel log was created *from the trip itself*. Distance and fuel now feed analytics with zero re-entry."

## 4:45 · Maintenance loop (step 8)
Fleet → Maintenance → New: Oil Change on Van-05 → save → show Van-05 **In Shop** and absent from a fresh trip's dropdown → back, **Close** → Available.
> "Opening a job pulls the vehicle from the dispatch pool instantly; closing releases it — unless another job is still open, or the vehicle was retired meanwhile. The edge cases are handled."

## 5:15 · Analytics + export (step 9)
Reporting → Vehicle Costs & ROI: point at Van-05's fuel efficiency (**10.0 km/L** — 150 km / 15 L), operational cost, ROI. Select rows → ⚙ Export → CSV downloads. Flash Trip Analysis pivot/graph.
> "Distance over fuel, fuel plus maintenance as operational cost, and ROI against acquisition — computed live, chartable, and CSV-exportable for the analyst."

## 5:45 · RBAC close (if time) & closing line
Quick re-login as `analyst@transitops.demo`: same data, read-only, no edit buttons.
> "Four roles, six models, sixteen enforced business rules, full audit trail — built in eight hours on Odoo because we spent our time on the rules, not on plumbing. Happy to break it live if you'd like to try."

## 7 · Judge Q&A crib (answers in one breath)
- **Scaling?** "Postgres + Odoo ORM; every rule is a server-side constraint, so a mobile driver app can hit the same JSON-RPC API tomorrow with identical guarantees."
- **Race conditions?** "Dispatch re-reads live statuses inside one transaction — second dispatcher gets a clean error, never a corrupt state."
- **Why Odoo / what did you actually build?** "Auth, RBAC plumbing, CRUD UI, export and responsiveness are framework; the six domain models, the state machines, and all sixteen business rules are ours — that trade is the architecture decision."
- **Tests?** "A manual matrix of ~50 cases run before each merge, plus automated TransactionCase tests for the core rules." *(only if D3 shipped them — else drop the second clause)*
- **What would you add with a week?** "License-expiry email crons, GPS trip tracking, and per-region record rules — the model layer already supports all three."
- **Team process?** "Contract-first: schemas, method specs and file ownership frozen at hour zero; four parallel branches; three checkpoint merges; zero merge conflicts."
