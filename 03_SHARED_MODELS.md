# 03 — SHARED MODEL INTERFACES

`02` defines the *schema*; this file defines the *social contract* around each model: who owns it, who consumes what, what events it emits, and what is frozen. "Provides" fields are stable API — renaming one mid-hackathon is a contract change (`00` §12).

---

## VEHICLE — owner D1
- **Provides (read) to:** D3 (`status`, `max_load_kg`, `odometer_km`, `name`, `registration_no`), D4 (`status`, `vehicle_type`, `region`, all financial computes, `acquisition_cost`), D1-maintenance (`status`).
- **Accepts writes from:** D3 → `status` (`on_trip`/`available` via trip actions only), `odometer_km` (on complete only); D1-maintenance → `status` (`in_shop`/`available`).
- **Events (side effects others rely on):** stored financial computes recompute automatically when fuel logs, maintenance costs, or completed trips change — D4's dashboard/reports need **no code** for this, only reads.
- **Depends on:** fuel.log, maintenance, trip (via One2many aggregation only — no method calls).
- **Frozen surface:** field names/keys in `02` §1, `action_retire()` signature, E-01/E-07/E-12 semantics.

## DRIVER — owner D2
- **Provides (read) to:** D3 (`status`, `license_expiry`, `is_license_valid`, `name`), D4 dashboard (`status`).
- **Accepts writes from:** D3 → `status` (`on_trip`/`available` via trip actions only).
- **Events:** none outbound. Suspension/off-duty immediately removes the driver from the dispatch pool purely via the `status` domain — no coordination needed.
- **Warning to consumers:** `is_license_valid` is **non-stored** (time-dependent). D3 must validate expiry server-side by comparing `license_expiry` with `fields.Date.context_today(self)` — never trust only the UI domain.
- **Frozen surface:** `02` §2 fields, four `action_*` button signatures, E-05/E-11/E-13.

## TRIP — owner D3 (the orchestrator)
- **Provides (read) to:** D4 (`state`, `actual_distance_km`, `revenue`, `vehicle_id`, `driver_id`, `dispatch_datetime` — for dashboard counts and Reporting pivots), D1 (aggregation into vehicle computes).
- **Writes (documented, exclusive):** `vehicle.status`, `vehicle.odometer_km`, `driver.status` — only inside `action_dispatch/complete/cancel`; and **creates** `transitops.fuel.log` records (`source='trip'`) on completion.
- **Consumes:** vehicle (`status`, `max_load_kg`, `odometer_km`), driver (`status`, `license_expiry`), sequence `seq_transitops_trip` (frozen in skeleton).
- **Frozen surface:** `state` keys, three `action_*` signatures, `actual_distance_km`/`revenue` names (D4 pivots reference them), E-02..E-06/E-09/E-14.

## MAINTENANCE — owner D1
- **Provides (read) to:** D4 (`cost`, `state`, `vehicle_id`, `date` for reports), vehicle computes.
- **Writes:** `vehicle.status` per BR-09/BR-10/BR-16.
- **Consumes:** vehicle `status`.
- **Frozen surface:** `state` keys (`open/done/cancelled`), `action_close()`/`action_cancel()`, E-08.

## FUEL.LOG — owner D4
- **Provides:** `liters`, `cost`, `date`, `vehicle_id` → aggregated by D1's vehicle computes and D4's own graphs.
- **Accepts creates from:** D3 (`trip.action_complete`), with fields exactly: `vehicle_id`, `trip_id`, `date` (today), `liters=fuel_consumed_l`, `cost=fuel_cost`, `odometer_km=end_odometer_km`, `source='trip'`.
- **Frozen surface:** those creation field names, E-10.

## EXPENSE — owner D4
- Pure leaf. Provides `amount`/`expense_type` for the "other expenses" total and analyst views. No one writes to it but D4 (and users).

## SECURITY GROUPS — defined in frozen skeleton, verified by D2
- Provide XML IDs consumed by everyone's `groups=` attributes and by demo users: `transitops.group_transitops_fleet_manager`, `..._dispatcher`, `..._safety_officer`, `..._analyst`.

## Cross-cutting stability rules
1. Anything marked 👁 in `02` or "Provides/Frozen" here is API. Add fields freely inside your own model; never rename/retype/remove a provided one.
2. No developer calls another owner's `_private()` method — only `action_*` methods and direct reads/writes documented above (full matrix in `06`).
3. If you need new data from someone else's model, request the field from its owner; they add it, you consume it.
