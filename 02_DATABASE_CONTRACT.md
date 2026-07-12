# 02 — DATABASE CONTRACT (authoritative schema)

Every field below is written with enough precision that Claude Code can generate the model file deterministically. Column "Def" gives the exact Odoo definition parameters. **Selection keys, field names and defaults are frozen** (change = Contract Change Protocol, `00` §12). All monetary values are Float in ₹. All models below except fuel.log/expense inherit `mail.thread`.

Legend: ✱ = required, 🔒 = readonly in UI, ⚙ = computed (store=True unless noted), 👁 = fields other developers read (public), ✍ = fields another owner may WRITE (only where stated).

---

## 1. `transitops.vehicle` — table `transitops_vehicle` — Owner: **D1**

`_name = 'transitops.vehicle'`, `_description = 'Vehicle'`, `_inherit = ['mail.thread']`, `_order = 'name'`, `_rec_names_search = ['name', 'registration_no']`

| Field | Def | Notes |
|---|---|---|
| `name` ✱👁 | `Char(required=True)` | Vehicle Name/Model, e.g. "Tata Ace Van-05" |
| `registration_no` ✱👁 | `Char(required=True, index=True, copy=False)` | BR-01 unique (SQL) |
| `vehicle_type` ✱👁 | `Selection([('truck','Truck'),('van','Van'),('bus','Bus'),('car','Car'),('bike','Bike')], required=True, default='van')` | dashboard filter dimension |
| `region` 👁 | `Selection([('north','North'),('south','South'),('east','East'),('west','West'),('central','Central')], default='west')` | dashboard filter dimension |
| `max_load_kg` ✱👁 | `Float(required=True)` | BR-05 input; must be > 0 (E-12 constrains) |
| `odometer_km` 👁 ✍(D3) | `Float(default=0.0, tracking=True)` | Trip `action_complete` writes this (BR-07) |
| `acquisition_cost` 👁 | `Float(default=0.0)` | BR-15 denominator |
| `status` ✱🔒👁 ✍(D1 maint, D3 trip) | `Selection([('available','Available'),('on_trip','On Trip'),('in_shop','In Shop'),('retired','Retired')], default='available', required=True, index=True, tracking=True)` | BR-12: readonly everywhere; mutated only by documented methods |
| `notes` | `Text()` | |
| `active` | `Boolean(default=True)` | archive support |
| `trip_ids` | `One2many('transitops.trip','vehicle_id')` | |
| `maintenance_ids` | `One2many('transitops.maintenance','vehicle_id')` | |
| `fuel_log_ids` | `One2many('transitops.fuel.log','vehicle_id')` | |
| `expense_ids` | `One2many('transitops.expense','vehicle_id')` | |
| `total_fuel_cost` ⚙👁 | `Float(compute='_compute_financials', store=True)` | Σ `fuel_log_ids.cost` |
| `total_fuel_liters` ⚙ | idem | Σ `fuel_log_ids.liters` |
| `total_maintenance_cost` ⚙👁 | idem | Σ `maintenance_ids.cost` where state ≠ cancelled |
| `total_operational_cost` ⚙👁 | idem | BR-14 = fuel + maintenance |
| `total_expense_other` ⚙ | idem | Σ `expense_ids.amount` (shown separately; NOT in op-cost per spec §3.7) |
| `total_distance_km` ⚙ | idem | Σ `trip_ids.actual_distance_km` where state = completed |
| `total_revenue` ⚙ | idem | Σ `trip_ids.revenue` where state = completed |
| `fuel_efficiency_kmpl` ⚙👁 | idem | `total_distance_km / total_fuel_liters`, 0.0 if liters = 0, round 2 |
| `roi_pct` ⚙👁 | idem | BR-15: `(total_revenue - total_operational_cost) / acquisition_cost * 100`, 0.0 if cost = 0, round 1 |

`@api.depends`: `'fuel_log_ids.cost','fuel_log_ids.liters','maintenance_ids.cost','maintenance_ids.state','trip_ids.state','trip_ids.actual_distance_km','trip_ids.revenue','acquisition_cost'`

SQL constraints: `('registration_unique','unique(registration_no)', <E-01 text>)`
Python constraints: `_check_max_load` (E-12: `max_load_kg > 0`).
Methods (spec in `04`): `action_retire()`.

## 2. `transitops.driver` — table `transitops_driver` — Owner: **D2**

`_inherit = ['mail.thread']`, `_order = 'name'`

| Field | Def | Notes |
|---|---|---|
| `name` ✱👁 | `Char(required=True)` | |
| `license_no` ✱👁 | `Char(required=True, index=True, copy=False)` | unique (SQL, E-11) |
| `license_category` ✱ | `Selection([('lmv','LMV'),('hmv','HMV'),('both','LMV + HMV')], required=True, default='lmv')` | |
| `license_expiry` ✱👁 | `Date(required=True, tracking=True)` | BR-03 input |
| `phone` | `Char()` | |
| `safety_score` | `Float(default=80.0)` | 0–100 (E-13 constrains) |
| `status` ✱🔒👁 ✍(D3 trip) | `Selection([('available','Available'),('on_trip','On Trip'),('off_duty','Off Duty'),('suspended','Suspended')], default='available', required=True, index=True, tracking=True)` | BR-12 |
| `is_license_valid` ⚙(store=False)👁 | `Boolean(compute='_compute_is_license_valid')` | `license_expiry >= fields.Date.context_today(self)`; non-stored (time-dependent) — never use in stored domains; server checks compare dates directly |
| `notes` | `Text()` |
| `active` | `Boolean(default=True)` |
| `trip_ids` | `One2many('transitops.trip','driver_id')` |

SQL: `('license_unique','unique(license_no)', <E-11>)`. Python: `_check_safety_score` (0 ≤ score ≤ 100, E-13).
Methods: `action_set_off_duty()`, `action_set_available()`, `action_suspend()`, `action_reinstate()`.

## 3. `transitops.trip` — table `transitops_trip` — Owner: **D3**

`_inherit = ['mail.thread']`, `_order = 'id desc'`

| Field | Def | Notes |
|---|---|---|
| `name` 🔒 | `Char(default='New', copy=False, readonly=True)` | set in `create()` from sequence `seq_transitops_trip` → `TRIP/2026/0001` |
| `source` ✱ | `Char(required=True)` | |
| `destination` ✱ | `Char(required=True)` | |
| `vehicle_id` ✱👁 | `Many2one('transitops.vehicle', required=True, tracking=True)` | form domain: `[('status','=','available')]` (BR-02/04 UX layer) |
| `driver_id` ✱👁 | `Many2one('transitops.driver', required=True, tracking=True)` | form domain: `[('status','=','available')]` (BR-03/04 UX; expiry enforced server-side) |
| `vehicle_max_load_kg` | `Float(related='vehicle_id.max_load_kg')` | UI helper next to cargo field |
| `cargo_weight_kg` ✱ | `Float(required=True)` | BR-05 |
| `planned_distance_km` | `Float()` | |
| `revenue` | `Float(default=0.0)` | feeds BR-15 |
| `state` ✱🔒👁 | `Selection([('draft','Draft'),('dispatched','Dispatched'),('completed','Completed'),('cancelled','Cancelled')], default='draft', required=True, index=True, tracking=True)` | BR-12 |
| `dispatch_datetime` 🔒 | `Datetime(readonly=True, copy=False)` | stamped by dispatch |
| `complete_datetime` 🔒 | `Datetime(readonly=True, copy=False)` | stamped by complete |
| `start_odometer_km` 🔒 | `Float(readonly=True, copy=False)` | snapshot of vehicle odometer at dispatch |
| `end_odometer_km` | `Float(copy=False)` | entered before complete; `readonly="state != 'dispatched'"` in view |
| `actual_distance_km` ⚙👁 | `Float(compute='_compute_actual_distance', store=True)` | `max(end - start, 0)` when completed, else 0; depends `end_odometer_km,start_odometer_km,state` |
| `fuel_consumed_l` | `Float(copy=False)` | optional at completion |
| `fuel_cost` | `Float(copy=False)` | optional; used for auto fuel log |
| `notes` | `Text()` |

Python constraints: `_check_cargo_weight` (BR-05, E-02) on `cargo_weight_kg, vehicle_id`.
Overrides: `create()` (sequence), `unlink()` (BR-13, E-14).
Methods: `action_dispatch()`, `action_complete()`, `action_cancel()` — full specs in `04`.

## 4. `transitops.maintenance` — table `transitops_maintenance` — Owner: **D1**

`_inherit = ['mail.thread']`, `_order = 'date desc, id desc'`

| Field | Def | Notes |
|---|---|---|
| `service_type` ✱ | `Selection([('oil_change','Oil Change'),('tyres','Tyres'),('brakes','Brakes'),('engine','Engine'),('electrical','Electrical'),('general','General Service'),('other','Other')], required=True, default='general')` | |
| `vehicle_id` ✱👁 | `Many2one('transitops.vehicle', required=True, tracking=True)` | form domain: `[('status','=','available')]` (BR-16 UX) |
| `date` ✱ | `Date(required=True, default=fields.Date.context_today)` | |
| `cost` 👁 | `Float(default=0.0, tracking=True)` | feeds BR-14 |
| `state` ✱🔒 | `Selection([('open','Open'),('done','Done'),('cancelled','Cancelled')], default='open', required=True, tracking=True)` | BR-12 |
| `description` | `Text()` |
| `display_name` | default (computed by Odoo) — list shows service_type + vehicle |

Behavior: `create()` — if `state == 'open'`: vehicle must be `available` (else E-08, BR-16), then write vehicle `status='in_shop'` (BR-09). `vehicle_id` readonly in view when `state != 'open'`.
Methods: `action_close()`, `action_cancel()` (BR-10 restore logic, incl. multi-open-record check) — specs in `04`.

## 5. `transitops.fuel.log` — table `transitops_fuel_log` — Owner: **D4**

`_order = 'date desc, id desc'`

| Field | Def | Notes |
|---|---|---|
| `vehicle_id` ✱👁 | `Many2one('transitops.vehicle', required=True, index=True, ondelete='cascade')` | domain `[('status','!=','retired')]` |
| `trip_id` | `Many2one('transitops.trip', ondelete='set null')` | domain `[('vehicle_id','=',vehicle_id)]` |
| `date` ✱ | `Date(required=True, default=fields.Date.context_today)` |
| `liters` ✱ | `Float(required=True)` | > 0 (E-10 constrains) |
| `cost` ✱ | `Float(required=True, default=0.0)` | ≥ 0 |
| `odometer_km` | `Float()` | optional reading at fill |
| `source` 🔒 | `Selection([('manual','Manual'),('trip','From Trip')], default='manual', readonly=True)` | trip auto-creation sets `'trip'` |

Python: `_check_liters` (E-10). **D3 is authorized to `create()` fuel logs** from `trip.action_complete` — the only cross-owner write besides statuses (documented in `06`).

## 6. `transitops.expense` — table `transitops_expense` — Owner: **D4**

| Field | Def | Notes |
|---|---|---|
| `vehicle_id` ✱ | `Many2one('transitops.vehicle', required=True, index=True, ondelete='cascade')` |
| `trip_id` | `Many2one('transitops.trip', ondelete='set null')` |
| `expense_type` ✱ | `Selection([('toll','Toll'),('parking','Parking'),('fine','Fine'),('misc','Miscellaneous')], required=True, default='toll')` |
| `amount` ✱ | `Float(required=True)` | ≥ 0 |
| `date` ✱ | `Date(required=True, default=fields.Date.context_today)` |
| `description` | `Char()` |

## 7. Relations & Indexes Summary

FKs (many2one): trip→vehicle, trip→driver, maintenance→vehicle, fuel.log→vehicle (+optional trip), expense→vehicle (+optional trip). Odoo auto-indexes m2o columns. Explicit extra indexes: `registration_no`, `license_no`, vehicle `status`, driver `status`, trip `state`. Unique: registration_no, license_no.

## 8. State Transition Matrix (authoritative — see `01` §5 diagram)

| Object | From → To | Trigger (only path) |
|---|---|---|
| vehicle | available→on_trip | `trip.action_dispatch` |
| vehicle | on_trip→available | `trip.action_complete` / `action_cancel` |
| vehicle | available→in_shop | `maintenance.create(state=open)` |
| vehicle | in_shop→available | `maintenance.action_close/_cancel` (only if no other open record) |
| vehicle | available/in_shop→retired | `vehicle.action_retire` (blocked if on_trip, E-07) |
| driver | available→on_trip / back | trip actions |
| driver | available⇄off_duty | driver buttons |
| driver | available/off_duty→suspended / back | `action_suspend` / `action_reinstate` (suspend blocked while on_trip) |
| trip | draft→dispatched→completed; draft/dispatched→cancelled | trip buttons |
| maintenance | open→done / open→cancelled | maintenance buttons |

## 9. Expected Entities Mapping (spec §6 → implementation)

Users → `res.users` (built-in) · Roles → `res.groups` (4 custom, `security_groups.xml`) · Vehicles/Drivers/Trips/Maintenance Logs/Fuel Logs/Expenses → the six models above. Nothing else exists.
