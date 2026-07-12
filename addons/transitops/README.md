TransitOps — Developer 3 (Trips)

This module implements the transitops.trip model (Developer 3 scope) for the TransitOps hackathon.

What I added:
- models/trip.py — Trip model, constraints, create() sequence, action_dispatch, action_complete, action_cancel.
- views/trip_views.xml — list, form, search, action and menu.
- tests/test_business_rules.py — TransactionCase tests for key rules (overweight, dispatch, complete).
- Minimal stubs: models/vehicle.py, models/driver.py, models/fuel_log.py to allow local syntax checks and to support the trip tests; these are minimal and should be replaced by the owners' full implementations.

Status:
- Code compiled locally with: python -m compileall addons/transitops
- I could not run Odoo or the tests because Odoo is not installed in this environment.

How to run locally (on your machine):

1) Ensure you have a working Odoo 18 (or compatible) installation and odoo-bin available in PATH.

2) From the repository root (parent of 'addons/'), install the module with:

   ./odoo-bin -d transitops_test --addons-path=addons -i transitops --stop-after-init

3) Run the tests via the Odoo test runner with:

   ./odoo-bin -d transitops_test --addons-path=addons -i transitops --test-enable --stop-after-init

Notes & next steps:
- Replace the minimal 'vehicle', 'driver', and 'fuel_log' stubs with the full owner implementations (D1/D2/D4). The trip code expects the fields documented in docs/02_DATABASE_CONTRACT.md.
- If you prefer, I can prepare a Docker Compose that runs Postgres + Odoo and installs the module in this workspace (requires network). Ask and I will scaffold it.
