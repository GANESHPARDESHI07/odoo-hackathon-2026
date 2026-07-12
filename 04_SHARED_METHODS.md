# 04 — SHARED METHODS (behavioral specs)

Every public method in the system, specified precisely enough to implement and to test. Error codes (E-xx) refer to the verbatim messages in `16_CONTRACTS.md`. All methods operate on `self` recordsets (loop or `ensure_one()` as noted). All raise `UserError` for workflow misuse, `ValidationError` from constraints.

---

## transitops.trip (D3)

### `action_dispatch(self)` — BR-02/03/04/06
Preconditions (checked live, server-side, in this order — this is the concurrency guard):
1. `self.state == 'draft'` else UserError "Only draft trips can be dispatched."
2. `vehicle.status == 'available'` else E-03 (covers in_shop/retired/on_trip → BR-02, BR-04).
3. `driver.status == 'available'` else E-04 (covers suspended/off_duty/on_trip → BR-03, BR-04).
4. `driver.license_expiry >= fields.Date.context_today(self)` else E-05 (BR-03).
5. Cargo constraint already guaranteed by `_check_cargo_weight` (BR-05) at save time; do not re-raise here.

Effects (single transaction): `vehicle.status='on_trip'`; `driver.status='on_trip'`; `self.start_odometer_km = vehicle.odometer_km`; `self.dispatch_datetime = fields.Datetime.now()`; `self.state='dispatched'`. Returns True.

### `action_complete(self)` — BR-07/11
Preconditions: `state == 'dispatched'` else UserError "Only dispatched trips can be completed."; `end_odometer_km` truthy else E-09; `end_odometer_km >= start_odometer_km` else E-06.
Effects: `vehicle.odometer_km = end_odometer_km`; `vehicle.status='available'`; `driver.status='available'`; `complete_datetime = now()`; `state='completed'`; **if** `fuel_consumed_l > 0`: create `transitops.fuel.log` with the exact field mapping in `03` (fuel.log card). Returns True.

### `action_cancel(self)` — BR-08
Preconditions: `state in ('draft','dispatched')` else UserError "Completed trips cannot be cancelled."
Effects: if state was `dispatched` → `vehicle.status='available'`, `driver.status='available'`. Always `state='cancelled'`. (No odometer/fuel effects.) Returns True.

### `create(self, vals_list)` override
For each vals: if `name` missing or `'New'` → `vals['name'] = self.env['ir.sequence'].next_by_code('transitops.trip')`.

### `unlink(self)` override — BR-13
If any record `state != 'draft'` → E-14. Else super().

### `_check_cargo_weight` — `@api.constrains('cargo_weight_kg','vehicle_id')` — BR-05
If `cargo_weight_kg <= 0` → ValidationError "Cargo weight must be greater than zero." If `cargo_weight_kg > vehicle_id.max_load_kg` → E-02.

### `_compute_actual_distance` — depends `end_odometer_km, start_odometer_km, state`
`state == 'completed'` → `max(end - start, 0.0)` else `0.0`.

## transitops.maintenance (D1)

### `create(self, vals_list)` override — BR-09/16
For each record created with `state == 'open'` (default): if `vehicle.status != 'available'` → E-08; else write `vehicle.status = 'in_shop'`. (Chatter message optional nicety: "Vehicle sent to shop: <service_type>".)

### `action_close(self)` — BR-10
Precondition: `state == 'open'` else UserError "Only open maintenance can be closed."
Effects: `state='done'`; then `self._release_vehicle()`.

### `action_cancel(self)` — BR-10
Precondition: `state == 'open'`. Effects: `state='cancelled'`; `self._release_vehicle()`.

### `_release_vehicle(self)` (private, D1-internal)
For each record: if `vehicle.status == 'in_shop'` (i.e., not retired meanwhile) **and** no other `transitops.maintenance` exists with same vehicle, `state == 'open'`, `id != self.id` → `vehicle.status = 'available'`. Otherwise leave status unchanged. This is the multi-open-record guard.

## transitops.vehicle (D1)

### `action_retire(self)` — BR-16
Precondition: `status != 'on_trip'` else E-07. Effects: `status='retired'`. (Retiring an `in_shop` vehicle is allowed — that is the "unless retired" branch of BR-10.)

### `_compute_financials(self)` — BR-14/15
Per `02` §1 formulas. Guard both divisions by zero (return 0.0). Round: efficiency 2dp, roi 1dp. Include maintenance where `state != 'cancelled'`; distance/revenue only from `state == 'completed'` trips.

## transitops.driver (D2)

### `action_set_off_duty(self)` — precondition `status == 'available'` else UserError "Only available drivers can go off duty."; effect `status='off_duty'`.
### `action_set_available(self)` — precondition `status in ('off_duty','suspended')` is NOT enough: only from `off_duty` (reinstate handles suspended); effect `status='available'`.
### `action_suspend(self)` — precondition `status != 'on_trip'` else UserError "Drivers on an active trip cannot be suspended."; effect `status='suspended'`.
### `action_reinstate(self)` — precondition `status == 'suspended'`; effect `status='available'`.
### `_compute_is_license_valid` — `license_expiry >= fields.Date.context_today(self)`; store=False.
### `_cron_license_expiry_reminder(self)` — STRETCH ONLY (Sprint 3 green): find drivers with `license_expiry <= today + 30d`, post a chatter message / send mail template. Ships with `active=False` cron if built.

## transitops.fuel.log (D4)
### `_check_liters` — `@api.constrains('liters','cost')`: `liters <= 0` → E-10; `cost < 0` → "Fuel cost cannot be negative."

## transitops.expense (D4)
### `_check_amount` — `amount < 0` → "Expense amount cannot be negative."

---

## Button ↔ Method wiring (UI contract hook, details in `05`)
| Form | Buttons (visible when) |
|---|---|
| Trip | Dispatch (`state=='draft'`), Complete (`state=='dispatched'`), Cancel (`state in draft,dispatched`) |
| Maintenance | Close (`open`), Cancel (`open`) |
| Vehicle | Retire (`status != 'retired'`) |
| Driver | Set Off Duty (`available`), Set Available (`off_duty`), Suspend (`status not in on_trip,suspended`), Reinstate (`suspended`) — Suspend/Reinstate restricted to `groups="transitops.group_transitops_safety_officer"` |
