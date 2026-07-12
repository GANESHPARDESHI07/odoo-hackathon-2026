# 00 — PROJECT CONTRACT (THE LAW)

Every developer reads this file completely before writing a single line of code. Nothing in this file may be changed during the hackathon except through the Contract Change Protocol (§12). If code and contract disagree, the contract wins.

Read order for every team member: `00` → `16_CONTRACTS.md` (cheat sheet) → your own developer file (`07`–`10`) → skim `02`, `05`, `13`. The Integration Lead additionally owns `11`.

---

## 1. Locked Stack Decisions

| Decision | Value | Rationale |
|---|---|---|
| Framework | Odoo **18 Community** (works on 17 with `<list>`→`<tree>` swap; if organizers mandate 19, patterns are identical) | Confirm the version verbally at minute 0:05. Whatever is confirmed goes here in ink. |
| Architecture | **One single addon module: `transitops`** | 4 modules = manifest/dependency hell. One module + file-level ownership + Hour-0 skeleton = near-zero merge conflicts. |
| Module path | `addons/transitops/` inside the repo | Repo root is the addons path. |
| Dependencies | `base`, `mail`, `web` only | `mail` gives chatter, tracking, attachments (= "vehicle document management" bonus for free). No other deps allowed. |
| Auth | Odoo built-in login (email + password) | Mandatory deliverable 1 is free. Never build custom auth. |
| RBAC | 4 security groups + ACL CSV (see §10) | Record rules only as stretch. |
| Currency | Plain `Float` fields, labels show "(₹)" | No `res.currency`/Monetary complexity in 8 hours. |
| Charts | Odoo native `graph` + `pivot` views | Satisfies "Charts and visual analytics" deliverable. **Nobody installs chart.js.** |
| CSV export | Odoo native list export (⚙ → Export) | Mandatory deliverable, zero code. |
| Dashboard | One OWL client action with KPI cards (Dev 4) | Working stub ships in the Hour-0 skeleton; fallback plan in `21`. |
| Integration Lead | **Developer 1** | Fleet models stabilize first; merge crunches don't collide with D1's peak load. |
| Tests | Manual QA matrix (`12`) mandatory; one automated `TransactionCase` = stretch | |

## 2. Repository Layout

```
transitops-hackathon/            (repo root = odoo addons_path entry)
├── CLAUDE.md                    (Claude Code project memory — from kit)
├── docs/                        (this entire Engineering Kit)
├── addons/
│   └── transitops/              (THE module — structure in §3)
└── README.md                    (submission readme, written Hour 7)
```

## 3. Module Structure & File Ownership

**The single most important rule of this hackathon: you only ever edit files you own.** If a change is needed in a file you don't own, you post a request to its owner (or the Lead) in team chat — you never "quickly fix it yourself."

| File | Owner | Notes |
|---|---|---|
| `__init__.py`, `__manifest__.py` | **LEAD (frozen)** | Written once at Hour 0. All data files pre-listed. Never edited again except by Lead via §12. |
| `models/__init__.py` | **LEAD (frozen)** | All 6 model imports pre-listed. |
| `security/security_groups.xml` | **LEAD (frozen)** | All 4 groups pre-created (CSV depends on them). |
| `security/ir.model.access.csv` | **LEAD (frozen)** | Full 30-row matrix pre-created (§10). |
| `security/record_rules.xml` | Dev 2 | Ships empty; stretch only. |
| `data/ir_sequence.xml` | **LEAD (frozen)** | Trip sequence pre-created. |
| `views/menus.xml` | **LEAD (frozen)** | Root + section menus only. Loaded FIRST. Leaf `menuitem`s live in owner view files. |
| `models/vehicle.py`, `models/maintenance.py`, `views/vehicle_views.xml`, `views/maintenance_views.xml` | **Dev 1** | |
| `models/driver.py`, `views/driver_views.xml`, `security/record_rules.xml`, license cron/mail (stretch) | **Dev 2** | |
| `models/trip.py`, `views/trip_views.xml`, `tests/test_business_rules.py` (stretch) | **Dev 3** | |
| `models/fuel_log.py`, `models/expense.py`, `views/fuel_expense_views.xml`, `views/dashboard_views.xml`, `static/src/dashboard/*`, `demo/demo_data.xml`, `report/*` (stretch) | **Dev 4** | |

Full tree:

```
addons/transitops/
├── __init__.py                    [LEAD]
├── __manifest__.py                [LEAD]
├── security/
│   ├── security_groups.xml        [LEAD]
│   ├── ir.model.access.csv        [LEAD]
│   └── record_rules.xml           [D2]
├── data/
│   └── ir_sequence.xml            [LEAD]
├── demo/
│   └── demo_data.xml              [D4]
├── models/
│   ├── __init__.py                [LEAD]
│   ├── vehicle.py                 [D1]
│   ├── maintenance.py             [D1]
│   ├── driver.py                  [D2]
│   ├── trip.py                    [D3]
│   ├── fuel_log.py                [D4]
│   └── expense.py                 [D4]
├── views/
│   ├── menus.xml                  [LEAD]
│   ├── vehicle_views.xml          [D1]
│   ├── maintenance_views.xml      [D1]
│   ├── driver_views.xml           [D2]
│   ├── trip_views.xml             [D3]
│   ├── fuel_expense_views.xml     [D4]
│   └── dashboard_views.xml        [D4]
├── static/src/dashboard/
│   ├── dashboard.js               [D4]
│   ├── dashboard.xml              [D4]
│   └── dashboard.scss             [D4]
└── tests/
    ├── __init__.py                [D3]
    └── test_business_rules.py     [D3, stretch]
```

## 4. Naming Conventions (non-negotiable)

- **Models:** `transitops.<noun>` singular — `transitops.vehicle`, `transitops.driver`, `transitops.trip`, `transitops.maintenance`, `transitops.fuel.log`, `transitops.expense`.
- **Python classes:** `TransitopsVehicle`, etc. Files: one model per file, snake_case filename.
- **Fields:** snake_case. Many2one ends `_id`, One2many/Many2many ends `_ids`. Dates end `_date` or are self-evident (`license_expiry`). Datetimes end `_datetime`. Quantities carry units: `max_load_kg`, `odometer_km`, `fuel_consumed_l`, `planned_distance_km`.
- **Workflow field name:** `state` on Trip and Maintenance (workflow objects); `status` on Vehicle and Driver (operational condition). Never mix.
- **XML IDs:** `view_transitops_<model>_<type>` (`view_transitops_vehicle_list`), `action_transitops_<model>` (`action_transitops_vehicle`), `menu_transitops_<name>`, `group_transitops_<role>`, `seq_transitops_trip`.
- **Methods:** public buttons `action_<verb>()`; computes `_compute_<field>()`; constraints `_check_<thing>()`; helpers `_<verb>_...()`. Private (`_`) methods are never called across model files (see `06`).
- **Menus sequence numbers:** Dashboard=1, Operations=10, Fleet=20, Drivers=30, Finance=40, Reporting=50.

## 5. Canonical Status Values (selection keys are law)

| Model | Field | Keys (exact) | Default |
|---|---|---|---|
| Vehicle | `status` | `available`, `on_trip`, `in_shop`, `retired` | `available` |
| Driver | `status` | `available`, `on_trip`, `off_duty`, `suspended` | `available` |
| Trip | `state` | `draft`, `dispatched`, `completed`, `cancelled` | `draft` |
| Maintenance | `state` | `open`, `done`, `cancelled` | `open` |

Labels shown to users: Available, On Trip, In Shop, Retired / Off Duty, Suspended / Draft, Dispatched, Completed, Cancelled / Open, Done, Cancelled.

**BR-12:** `status`/`state` are readonly in every view. Transitions happen ONLY through the `action_*` buttons defined in `04_SHARED_METHODS.md`. No exceptions — this is what makes the FSM demoable and safe.

## 6. Business Rules Registry (BR-xx — cite these IDs in code comments, commits, tests)

| ID | Rule | Enforced by | Owner |
|---|---|---|---|
| BR-01 | Vehicle registration number is unique | SQL constraint on `transitops.vehicle` | D1 |
| BR-02 | Retired / In Shop vehicles never appear in dispatch selection and cannot be dispatched | View domain + server check in `action_dispatch` | D3 (D1 provides `status`) |
| BR-03 | Drivers with expired license or `suspended` status cannot be assigned/dispatched | View domain + server check in `action_dispatch` | D3 (D2 provides fields) |
| BR-04 | A vehicle or driver already `on_trip` cannot be booked on another trip | View domain + server check in `action_dispatch` | D3 |
| BR-05 | `cargo_weight_kg` ≤ vehicle `max_load_kg` | `@api.constrains` on trip | D3 |
| BR-06 | Dispatching sets vehicle **and** driver `status = on_trip` | `action_dispatch` | D3 |
| BR-07 | Completing sets both back to `available` and writes trip end odometer to vehicle | `action_complete` | D3 |
| BR-08 | Cancelling a dispatched trip restores both to `available` | `action_cancel` | D3 |
| BR-09 | Creating an open maintenance record sets vehicle `status = in_shop` | `create()` override on maintenance | D1 |
| BR-10 | Closing/cancelling maintenance restores `available` — unless the vehicle was retired meanwhile or another open maintenance record exists | `action_close` / `action_cancel` | D1 |
| BR-11 | Trip end odometer ≥ start odometer; end odometer required to complete | `action_complete` | D3 |
| BR-12 | Status transitions only via action buttons | readonly fields + methods | All |
| BR-13 | Only `draft` trips may be deleted | `unlink()` override | D3 |
| BR-14 | Operational cost per vehicle = Σ fuel cost + Σ maintenance cost (auto-computed) | stored computes on vehicle | D1 |
| BR-15 | Vehicle ROI % = (Σ trip revenue − operational cost) / acquisition cost × 100, 0 when cost is 0 | stored compute on vehicle | D1 |
| BR-16 | Maintenance can be opened only for vehicles currently `available`; vehicles can be retired only when not `on_trip` | maintenance `create()`, `action_retire` | D1 |

## 7. Persona → Role Mapping (say this to judges)

The spec's "Driver" *persona* creates and monitors trips — that is a **Dispatcher** role. Actual drivers are data records (`transitops.driver`), not users.

| Spec persona | Odoo group | XML ID |
|---|---|---|
| Fleet Manager | Fleet Manager | `group_transitops_fleet_manager` |
| "Driver" (dispatch persona) | Dispatcher | `group_transitops_dispatcher` |
| Safety Officer | Safety Officer | `group_transitops_safety_officer` |
| Financial Analyst | Financial Analyst | `group_transitops_analyst` |

## 8. Coding Standards

- Python: PEP 8, 4-space indent, no `print()` — use `_logger = logging.getLogger(__name__)`.
- All user-facing errors: `ValidationError` (data rules) / `UserError` (workflow misuse) from `odoo.exceptions`, message text taken **verbatim from the E-xx table in `16_CONTRACTS.md`**, wrapped in `_()` for translation.
- Every constraint/action carries a one-line comment citing its BR-ID: `# BR-05`.
- Odoo 18 view rules: list views use `<list>` (not `<tree>`); **`attrs`/`states` do not exist** — use expression attributes: `invisible="state != 'draft'"`, `readonly="state != 'draft'"`, `required="state == 'dispatched'"`.
- Vehicle, Driver, Trip, Maintenance inherit `mail.thread` (`_inherit = ['mail.thread']`) with `tracking=True` on `status`/`state` and key fields → free audit log + attachments.
- No `sudo()` unless documented in `06`. No monkey-patching. No new dependencies.
- Commits: `feat(vehicle): BR-01 unique registration + list/form views` — see `13`.

## 9. Merge Rules (digest — full workflow in `13`)

1. Branches: `main` + `feat/d1-fleet`, `feat/d2-drivers`, `feat/d3-trips`, `feat/d4-finance`. Nobody pushes to `main` except the Lead.
2. Merges only at checkpoints (2:15, 4:45, 6:15) by the Lead, in order d1→d2→d3→d4.
3. A branch is mergeable only if: module installs/upgrades clean on your machine, your Self-QA checklist passed, and you posted a `17` status + `18` merge note.
4. Conflicts in a file resolve in favor of its **owner**. Conflicts in frozen files mean someone broke rule §3 — Lead's version wins, violator re-applies via request.

## 10. Access Matrix (implemented in frozen CSV — reference)

R/W/C/U = read/write/create/unlink. FM=Fleet Manager, DP=Dispatcher, SO=Safety Officer, FA=Analyst. `base.group_system` gets full access to everything.

| Model | FM | DP | SO | FA |
|---|---|---|---|---|
| vehicle | RWCU | R | R | R |
| driver | R | R | RWCU | R |
| trip | RW | RWCU | R | R |
| maintenance | RWCU | R | R | R |
| fuel.log | RWC | RWC | R | R |
| expense | RWC | RWC | R | R |

Menu visibility follows the same logic (`groups=` on menuitems/actions where it adds clarity; default: all four groups see the root menu).

## 11. Bonus Feature Triage (pre-decided — do not relitigate at Hour 5)

| Bonus | Verdict | How |
|---|---|---|
| Search, filters, sorting | **CLAIM — free** | Search views + group-bys are mandatory in `05` anyway. |
| Charts & analytics | **CLAIM — cheap** | graph/pivot views (already mandatory deliverable). |
| Vehicle document management | **CLAIM — free** | Chatter attachments from `mail.thread`. Say it in the demo. |
| PDF export | Stretch (D4, Sprint 3 only if green) | One QWeb "Vehicle Cost Card" report. |
| Email reminders for expiring licenses | Stretch (D2, Sprint 3 only if green) | Cron + mail template; demo via manual trigger. |
| Dark mode | **SKIP** | Not native in Community; time sink. |

## 12. Contract Change Protocol

A contract change = any change to: frozen files, model/field names, selection keys, method signatures in `04`, XML IDs in `05`/`16`, or the access matrix. Procedure: (1) requester posts `CONTRACT CHANGE REQUEST: <what/why>` in team chat, (2) Lead approves/rejects within 5 minutes, (3) Lead edits the frozen file / contract doc on `main`, announces `CONTRACT v+1: <summary>`, (4) everyone pulls `main` before their next commit. Undocumented drift is treated as a bug.

## 13. Definition of Done (per task)

A task is done only when: module upgrades clean (`-u transitops`, zero traceback), the feature works through the UI, relevant BR-xx behaves per the QA matrix, status field readonly rule holds, code cites BR-IDs, and the change is committed on your branch with a conventional message. "Works in Claude's explanation" is not done — **only the running Odoo instance counts.**

## 14. Documentation & Communication Conventions

- Status posts in team chat at each checkpoint using `17_IMPLEMENTATION_STATUS_TEMPLATE.md`.
- Merge notes using `18_MERGE_NOTES_TEMPLATE.md` accompany every merge request.
- Blockers are announced the minute they exceed **10 minutes** of solo debugging. Silence is the only unforgivable failure mode.
- All prompts to Claude Code follow the conventions in `20_CLAUDE_BEST_PRACTICES.md`; your role prompt is your developer file.
