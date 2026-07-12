# 05 — UI CONTRACT

Note on the mockup: the Excalidraw board is a live canvas that can't be parsed programmatically; this contract maps the problem statement onto standard Odoo backend patterns (which is what judges at an Odoo hackathon expect to see). If the mockup shows a materially different layout, reconcile at minute 0:10 and record deltas here via the change protocol.

## 1. Menu Tree (root/sections frozen in `views/menus.xml`; leaves live in owner files)

```
TransitOps (menu_transitops_root)
├── Dashboard        seq 1   [D4: menu_transitops_dashboard → action_transitops_dashboard (client)]
├── Operations       seq 10  (menu_transitops_operations)
│   └── Trips                [D3: menu_transitops_trip → action_transitops_trip]
├── Fleet            seq 20  (menu_transitops_fleet)
│   ├── Vehicles             [D1: menu_transitops_vehicle → action_transitops_vehicle]
│   └── Maintenance          [D1: menu_transitops_maintenance → action_transitops_maintenance]
├── Drivers          seq 30  (menu_transitops_drivers)
│   └── Drivers              [D2: menu_transitops_driver → action_transitops_driver]
├── Finance          seq 40  (menu_transitops_finance)
│   ├── Fuel Logs            [D4: menu_transitops_fuel_log → action_transitops_fuel_log]
│   └── Expenses             [D4: menu_transitops_expense → action_transitops_expense]
└── Reporting        seq 50  (menu_transitops_reporting)
    ├── Trip Analysis        [D4: menu_transitops_trip_analysis → action_transitops_trip_analysis (pivot,graph)]
    └── Vehicle Costs & ROI  [D4: menu_transitops_vehicle_analysis → action_transitops_vehicle_analysis (list)]
```

## 2. Global View Standards
- Odoo 18: list tag is `<list>`. No `attrs`/`states` — expression attributes only.
- Every model ships **minimum**: list + form + search view. Actions declare `view_mode="list,form"` (plus kanban/pivot/graph where specified).
- Every form for Vehicle/Driver/Trip/Maintenance: `<header>` with action buttons + `<field name="state|status" widget="statusbar"/>` (readonly — BR-12), `<sheet>` with a 2-column `<group>`, chatter block at the bottom (`<chatter/>` in v18).
- Status/state in **list views**: `widget="badge"` with decorations below.
- Action `help` attribute set on every act_window with a friendly empty-state line (e.g., *"Register your first vehicle to start dispatching trips."*) — cheap polish judges notice.
- Money fields labeled with `(₹)` in `string=`.

## 3. Color Semantics (decorations — identical across the app)
| Value | List decoration / badge |
|---|---|
| available / completed / done | `decoration-success` |
| on_trip / dispatched | `decoration-info` |
| in_shop / open / draft | `decoration-warning` |
| retired / suspended / cancelled | `decoration-danger` (retired: also `decoration-muted` acceptable) |
| off_duty | `decoration-muted` |

## 4. Per-Model Requirements

**Vehicle (D1):** list: name, registration_no, vehicle_type, region, status(badge), odometer_km, total_operational_cost, fuel_efficiency_kmpl, roi_pct. Form: header Retire button + statusbar; group A (name, registration_no, vehicle_type, region), group B (max_load_kg, odometer_km, acquisition_cost); notebook page "Financials" (readonly computed fields), pages Trips / Maintenance / Fuel (one2many lists readonly). Search: filters per status (×4), per type; **filters + group_by: type, status, region** (spec §3.2 requirement); Kanban view optional Sprint 3.

**Driver (D2):** list: name, license_no, license_category, license_expiry, safety_score, status(badge), `is_license_valid` (boolean toggle, readonly). Form: header 4 buttons per `04` + statusbar. Search: status filters + **"License Expired"** filter `[('license_expiry','&lt;', context_today().strftime('%Y-%m-%d'))]` + group_by status/category.

**Trip (D3):** list: name, source, destination, vehicle_id, driver_id, cargo_weight_kg, state(badge), dispatch_datetime. Form: header Dispatch/Complete/Cancel + statusbar (`statusbar_visible="draft,dispatched,completed"`); group A (source, destination, vehicle_id, driver_id), group B (cargo_weight_kg with vehicle_max_load_kg beside it, planned_distance_km, revenue); section "Completion" visible when `state in ('dispatched','completed')`: start_odometer_km, end_odometer_km, actual_distance_km, fuel_consumed_l, fuel_cost. `end_odometer_km` readonly unless dispatched. Search: filters per state + group_by vehicle/driver.

**Maintenance (D1):** list: display_name/service_type, vehicle_id, date, cost, state(badge). Form: Close/Cancel buttons + statusbar; vehicle_id readonly when not open.

**Fuel Log / Expense (D4):** simple lists + forms; fuel list shows vehicle, date, liters, cost, source(badge), trip_id. Search group_by vehicle/month.

## 5. Dashboard (D4 — client action `transitops.dashboard`)
Layout: responsive card grid (2 rows × 4). Cards, exactly these KPIs and definitions (LOCKED — QA verifies the math):

| Card | Definition (domain) |
|---|---|
| Total Fleet | vehicles `status != retired` |
| Available Vehicles | `status = available` |
| In Maintenance | `status = in_shop` |
| On Trip | `status = on_trip` |
| Active Trips | trips `state = dispatched` |
| Pending Trips | `state = draft` |
| Drivers On Duty | drivers `status in (available, on_trip)` |
| Fleet Utilization % | On Trip ÷ Total Fleet × 100, 1dp, 0 if fleet empty |

Behavior: each card is clickable → opens the corresponding filtered list (`action.doAction` with domain). Two `<select>` filters at top — Vehicle Type, Region — re-run the vehicle-based counts with the extra domain (spec §3.2 filters). Trips/drivers cards ignore these filters (state that in a caption). Styling: plain SCSS cards, Odoo variables, no external libs.

## 6. Reporting Views (D4)
- `action_transitops_trip_analysis` on trip, `view_mode="pivot,graph"`, default measures `actual_distance_km`, `revenue`; rows vehicle_id, cols month(dispatch_datetime). Graph default bar.
- `action_transitops_vehicle_analysis` on vehicle, list view `view_transitops_vehicle_analysis_list`: name, registration_no, total_distance_km, total_fuel_liters, fuel_efficiency_kmpl, total_fuel_cost, total_maintenance_cost, total_operational_cost, total_revenue, roi_pct. **This list is the CSV-export demo surface** (select all → ⚙ Export).
- Fuel graph optional: graph view on fuel.log (cost by month/vehicle).

## 7. Responsiveness & Login
Both come from the framework: demo the login page as deliverable 1 ("secure session-based auth with role-based menus"), and resize the browser once during the demo to show the responsive backend. Zero custom code — say so proudly, it's an architecture decision, not a shortcut.
