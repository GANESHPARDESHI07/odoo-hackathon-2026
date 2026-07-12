# 06 — API & INTERACTION CONTRACT

In an Odoo module the "API" between developers is the set of model methods, permitted cross-model reads/writes, and the error surface. This file is the whitelist. **Anything not listed here is forbidden across ownership boundaries.**

## 1. Cross-Boundary Interaction Whitelist

| Caller | Target | Operation | Where allowed |
|---|---|---|---|
| D3 trip | vehicle.status | write `on_trip`/`available` | inside `action_dispatch/complete/cancel` only |
| D3 trip | vehicle.odometer_km | write | inside `action_complete` only |
| D3 trip | driver.status | write `on_trip`/`available` | inside trip actions only |
| D3 trip | driver.license_expiry, driver.status | read | dispatch validation |
| D3 trip | vehicle.status, max_load_kg, odometer_km | read | validation/snapshot |
| D3 trip | transitops.fuel.log | `create()` with the exact mapping in `03` | inside `action_complete` only |
| D1 maintenance | vehicle.status | write `in_shop`/`available` | `create()`, `_release_vehicle()` |
| D1 vehicle computes | fuel.log, maintenance, trip fields | read (via One2many depends) | `_compute_financials` |
| D4 dashboard | vehicle/driver/trip | `search_count` / `read_group` (read-only) | OWL via ORM service |
| D4 reports/demo | all models | read; demo XML creates records | pivots, `demo_data.xml` |
| Anyone | another owner's `action_*` methods | call | only where a view button in `05` wires it |

Explicitly forbidden: calling `_private()` methods across files; writing any field not listed above; `sudo()` (exception: none currently — if RBAC blocks a legitimate automated write during Sprint 2, raise a contract change rather than sudo-ing); overriding another owner's method via `_inherit` in your own file.

## 2. Error Surface (stable — QA tests assert these)
All blocking rules raise with the **verbatim E-xx texts in `16_CONTRACTS.md`**. Errors are part of the API: judges will trigger them; tests match on them; nobody rewords them unilaterally. `ValidationError` for data constraints (E-01/02/10/11/12/13), `UserError` for workflow misuse (E-03..E-09, E-14).

## 3. External API (talking point, not work)
Every model here is automatically exposed over Odoo's JSON-RPC/XML-RPC external API with the same ACLs — mention to judges that a mobile driver app could call `transitops.trip.action_complete` tomorrow with zero backend changes. Do **not** build custom HTTP controllers.

## 4. Override & Extension Policy
- You may override `create/write/unlink` **only on models you own**, and only for behaviors specified in `04`.
- Adding a field to your own model: free, no approval (append to `02` yourself post-hackathon; during, just announce).
- Adding a field you need on someone else's model: request → owner implements within their file.
- Changing anything on a frozen surface (`03` cards): Contract Change Protocol.

## 5. Transactional Guarantees
Each `action_*` executes in one Odoo transaction — a validation failure rolls back all status writes, so the system can never end half-dispatched. Dispatch's live re-read of `vehicle.status`/`driver.status` (see `04`) is the double-booking guard: the second of two racing dispatchers gets E-03/E-04 instead of a corrupt state. Say this sentence to the judges.
