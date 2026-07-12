# 16 — CONTRACTS CHEAT SHEET (print/pin this)

One page of everything frozen. Details live in `02`–`06`; disputes go to the Lead.

## Models & owners
`transitops.vehicle` D1 · `transitops.driver` D2 · `transitops.trip` D3 · `transitops.maintenance` D1 · `transitops.fuel.log` D4 · `transitops.expense` D4

## Status keys (exact)
vehicle.status: `available | on_trip | in_shop | retired` · driver.status: `available | on_trip | off_duty | suspended` · trip.state: `draft | dispatched | completed | cancelled` · maintenance.state: `open | done | cancelled`

## Public methods
trip: `action_dispatch` `action_complete` `action_cancel` · maintenance: `action_close` `action_cancel` · vehicle: `action_retire` · driver: `action_set_off_duty` `action_set_available` `action_suspend` `action_reinstate`

## Sanctioned cross-writes (everything else forbidden — `06`)
trip → vehicle.status, vehicle.odometer_km, driver.status, fuel.log create · maintenance → vehicle.status

## XML IDs
Actions: `action_transitops_vehicle | _maintenance | _driver | _trip | _fuel_log | _expense | _dashboard | _trip_analysis | _vehicle_analysis`
Menus: root `menu_transitops_root`; sections `_operations _fleet _drivers _finance _reporting`; leaves `menu_transitops_<model/report>`
Groups: `group_transitops_fleet_manager | _dispatcher | _safety_officer | _analyst` · Sequence: `seq_transitops_trip`

## Access matrix (R/W/C/U)
vehicle FM:RWCU DP/SO/FA:R · driver SO:RWCU others:R · trip DP:RWCU FM:RW SO/FA:R · maintenance FM:RWCU others:R · fuel/expense FM,DP:RWC SO,FA:R · group_system: everything

## KPI definitions (locked — `05` §5)
Fleet = status≠retired · Available/InShop/OnTrip by status · Active=dispatched, Pending=draft trips · On Duty = driver status ∈ {available,on_trip} · Utilization = OnTrip/Fleet ×100 (1dp)

## Error text registry (verbatim — wrap in `_()`)
| ID | Type | Text |
|---|---|---|
| E-01 | SQL | A vehicle with this registration number already exists. |
| E-02 | Validation | Cargo weight ({cargo} kg) exceeds the maximum load capacity of {vehicle} ({capacity} kg). |
| E-03 | User | Vehicle {vehicle} is not available for dispatch (current status: {status}). |
| E-04 | User | Driver {driver} is not available for dispatch (current status: {status}). |
| E-05 | User | Driver {driver}'s license expired on {date}. Assignment blocked. |
| E-06 | User | End odometer ({end} km) cannot be less than start odometer ({start} km). |
| E-07 | User | Vehicle {vehicle} cannot be retired while On Trip. |
| E-08 | User | Maintenance can only be opened for vehicles that are Available (current status: {status}). |
| E-09 | User | Enter the end odometer reading before completing the trip. |
| E-10 | Validation | Fuel quantity must be greater than zero. |
| E-11 | SQL | A driver with this license number already exists. |
| E-12 | Validation | Maximum load capacity must be greater than zero. |
| E-13 | Validation | Safety score must be between 0 and 100. |
| E-14 | User | Only draft trips can be deleted. |

({placeholders} formatted with real values; status placeholders use the human label.)

## Business rules
BR-01 unique reg · BR-02 no in_shop/retired dispatch · BR-03 no expired/suspended drivers · BR-04 no double-booking · BR-05 cargo ≤ capacity · BR-06 dispatch→on_trip both · BR-07 complete→available + odometer · BR-08 cancel restores · BR-09 open maint→in_shop · BR-10 close→available unless retired/other open · BR-11 end ≥ start odometer · BR-12 buttons-only transitions · BR-13 delete drafts only · BR-14 opcost=fuel+maint · BR-15 ROI formula · BR-16 maint needs available vehicle; retire blocked on_trip

## Demo credentials (seed)
admin (all groups) · fm@transitops.demo · dispatch@transitops.demo · safety@transitops.demo · analyst@transitops.demo — password `transitops`

## Frozen files (Lead-only)
`__manifest__.py` · both `__init__.py` · `security_groups.xml` · `ir.model.access.csv` · `data/ir_sequence.xml` · `views/menus.xml`
