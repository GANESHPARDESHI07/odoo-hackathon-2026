# 09 — DEVELOPER 3 · TRIP MANAGEMENT (the heart of the demo)

> Paste below the line into Claude Code, or say: *"Read docs/00, docs/02 §3, docs/04, docs/05 §4, docs/06 and docs/09_DEVELOPER_3.md, then follow 09."*

---

## ROLE
You are Developer 3 on a 4-person, 8-hour Odoo hackathon team building TransitOps. You own **Trip Management** — the orchestrator model that enforces most mandatory business rules (BR-02..BR-08, BR-11, BR-13) and drives the status automation the judges will score hardest. Your code is the demo's spine; correctness beats cleverness.

## READ FIRST
`docs/00_PROJECT_CONTRACT.md`, `docs/02_DATABASE_CONTRACT.md` §3 (+ skim §1, §2, §5 — you consume them), `docs/04_SHARED_METHODS.md` (trip section is your spec, follow it to the letter), `docs/06_API_CONTRACT.md` (your cross-writes are the whitelist's core), `docs/16_CONTRACTS.md` (E-02..E-06, E-09, E-14).

## OWNERSHIP
- **You may edit ONLY:** `addons/transitops/models/trip.py`, `views/trip_views.xml`, `tests/test_business_rules.py` (+ its `__init__`) as stretch.
- **You must NEVER edit:** manifest, `__init__` files (models), security files, menus.xml, vehicle/driver/maintenance/fuel/expense/dashboard files. You DO write `vehicle.status`, `vehicle.odometer_km`, `driver.status` and create fuel logs **from inside trip.py methods** — that's the sanctioned interaction (`06` §1) — but you never open those files.

## SCOPE

**Sprint 1 (0:30–2:15).** Acceptance: trips CRUD with sequence names and cargo validation.
1. Flesh out `transitops.trip` per `02` §3: all fields incl. related `vehicle_max_load_kg`, `create()` sequence override (`transitops.trip` code — sequence record already exists in skeleton), `_check_cargo_weight` (BR-05, E-02 + positive-cargo message), `_compute_actual_distance`, mail.thread + tracking.
2. `unlink()` override — BR-13/E-14.
3. Views per `05` §4: form with header buttons (Dispatch/Complete/Cancel — can call stub methods returning True this sprint), statusbar, Completion section with visibility/readonly expressions; list with state badges; search with state filters + group_by vehicle/driver. Domains on `vehicle_id`/`driver_id`: `[('status','=','available')]`.
4. Leaf menuitem `menu_transitops_trip` (parent `transitops.menu_transitops_operations`).

**Sprint 2 (2:45–4:45) — the money sprint.**
5. `action_dispatch()` EXACTLY per `04`: precondition order matters (state → vehicle E-03 → driver E-04 → license E-05), live re-reads for the concurrency guard, snapshot start odometer, stamp datetime, flip both statuses. Cite BR-IDs in comments.
6. `action_complete()` per `04`: E-09/E-06 guards, write vehicle odometer, restore statuses, stamp datetime, **auto-create fuel log** when `fuel_consumed_l > 0` with the exact field mapping from `03` (fuel.log card) — this is a scripted demo moment.
7. `action_cancel()` per `04` (BR-08).
8. Button visibility per `04` wiring table; `end_odometer_km` editable only when dispatched.
9. Integration self-test of the full spec §5 example workflow on your machine before Merge 2.

**Sprint 3 (5:15–6:15) — hardening.** Edge passes from `12` (double-dispatch race, cancel-draft, complete-without-odometer); friendly `help` text on the action; STRETCH if green: `tests/test_business_rules.py` — one `TransactionCase` with 3 tests (overweight blocked; dispatch flips both statuses; complete restores + writes odometer). Skeleton for it is in `12` Appendix A.

## CONTRACTS YOU EXPOSE (frozen)
`state` keys; `action_dispatch/complete/cancel` signatures; field names `actual_distance_km`, `revenue`, `vehicle_id`, `driver_id`, `dispatch_datetime` (D4's pivots and D1's vehicle computes read them); error texts E-02..E-06/E-09/E-14 verbatim.

## CONTRACTS YOU CONSUME
Vehicle: `status`, `max_load_kg`, `odometer_km` (read), `status`/`odometer_km` (write per `06`). Driver: `status`, `license_expiry` (read), `status` (write). Fuel log: `create()` with mapping `vehicle_id, trip_id, date=today, liters=fuel_consumed_l, cost=fuel_cost, odometer_km=end_odometer_km, source='trip'`. Sequence `seq_transitops_trip` (exists from Hour 0).

## IMPLEMENTATION NOTES / GOTCHAS
- **Server-side checks are the truth**; the view domains are UX only. A judge can hit Dispatch on a stale form — your live re-read in `action_dispatch` must catch it (say this in the demo).
- Don't re-validate cargo inside dispatch — the constraint already guarantees it at save (avoids double errors).
- `fields.Date.context_today(self)` for the license comparison; naive `date.today()` breaks under user timezones.
- Odoo 18 syntax rules per `00` §8; `readonly="state != 'dispatched'"` on `end_odometer_km`.
- All three actions: iterate `self` safely or `ensure_one()` (buttons pass single records; keep loops anyway for robustness).

## WORKFLOW LOOP / SELF-QA / GIT
Standard loop (plan → edit own files → `-u transitops` → click test → small commit `feat(trip): BR-06 dispatch automation`). Branch `feat/d3-trips` only.
Self-QA slice: upgrade clean · sequence names generate · overweight blocked with E-02 exact text · dispatch flips BOTH statuses (verify on vehicle/driver forms) · vehicle vanishes from a second trip's dropdown · expired-license driver blocked at dispatch (E-05) even if somehow selected · complete without end odometer → E-09; end < start → E-06 · complete restores statuses + vehicle odometer updated + fuel log auto-created · cancel dispatched restores both · delete non-draft blocked (E-14).

## STATUS OUTPUT / ESCALATION
`docs/17` template at checkpoints. If vehicle/driver stubs are missing a field you need, that's a `REQUEST TO <owner>` — never add it to their file yourself. Blocked >10 min → surface it.
