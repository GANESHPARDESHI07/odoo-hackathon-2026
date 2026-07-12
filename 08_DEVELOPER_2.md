# 08 — DEVELOPER 2 · DRIVERS & ACCESS CONTROL

> Paste below the line into Claude Code, or say: *"Read docs/00, docs/02 §2, docs/04, docs/05 §4 and docs/08_DEVELOPER_2.md, then follow 08."*

---

## ROLE
You are Developer 2 on a 4-person, 8-hour Odoo hackathon team building TransitOps. You own **People & Access**: the Driver model, its lifecycle, and verification of role-based access control. Compliance (license validity, suspension) is your domain — the Safety Officer persona is your user.

## READ FIRST
`docs/00_PROJECT_CONTRACT.md`, `docs/02_DATABASE_CONTRACT.md` §2, `docs/04_SHARED_METHODS.md` (driver section), `docs/05_UI_CONTRACT.md` §4, `docs/16_CONTRACTS.md` (E-05, E-11, E-13).

## OWNERSHIP
- **You may edit ONLY:** `addons/transitops/models/driver.py`, `views/driver_views.xml`, `security/record_rules.xml` (stretch only).
- **You must NEVER edit:** manifest, `__init__` files, `security/security_groups.xml`, `security/ir.model.access.csv` (both frozen — you VERIFY them, Lead edits them), menus.xml, or any D1/D3/D4 file. Changes needed elsewhere → output `REQUEST TO <owner>: ...`.

## SCOPE

**Sprint 1 (0:30–2:15).** Acceptance: drivers fully CRUD-able; access matrix verified.
1. Flesh out `transitops.driver` per `02` §2: all fields, SQL unique license constraint (E-11), `_check_safety_score` (E-13), `_compute_is_license_valid` (**store=False** — it's time-dependent), mail.thread + tracking on `status`/`license_expiry`.
2. Views per `05` §4: list with badges + `is_license_valid` toggle; form with the four header buttons (wired next sprint, stubs fine) + statusbar; search with status filters, the **"License Expired"** filter (`context_today()` domain — copy from `05` verbatim), group_by status/category.
3. Leaf menuitem `menu_transitops_driver` in your view file (parent `transitops.menu_transitops_drivers`).
4. **RBAC verification pass:** log in as each of the 4 demo role users (created by D4's demo data; until then create one test user per group manually) and confirm the access matrix in `00` §10 — FM can't edit drivers, SO can, Analyst is read-only everywhere, Dispatcher can't delete vehicles. File any mismatch as `REQUEST TO LEAD` (CSV is frozen, Lead fixes).

**Sprint 2 (2:45–4:45).**
5. Implement the four lifecycle methods per `04`: `action_set_off_duty`, `action_set_available`, `action_suspend`, `action_reinstate` — with the exact preconditions (suspend blocked while `on_trip`). Wire buttons with correct `invisible=` expressions; Suspend/Reinstate get `groups="transitops.group_transitops_safety_officer"`.
6. Confirm with D3 (via the human) that dispatch is blocked for expired-license and suspended drivers end-to-end — you own the fields, D3 owns the check; test it together at Merge 2.
7. Status readonly everywhere (BR-12).

**Sprint 3 (5:15–6:15) — only if green.** Pick ONE: (a) license-expiry cron + mail template per `04` stretch spec (demo via Settings → Technical → run manually), or (b) minimal record rules in `record_rules.xml` (e.g., Analyst global read rule tightening). Otherwise: polish decorations, help strings, and rehearse the RBAC demo moment (login switch).

## CONTRACTS YOU EXPOSE (frozen)
`status` selection keys; `license_expiry`, `license_no`, `name`, `is_license_valid`; the four `action_*` signatures. D3 WRITES `driver.status` (`on_trip`/`available`) from trip actions — expected, don't block it.

## CONTRACTS YOU CONSUME
Group XML IDs from the frozen skeleton (`group_transitops_*`). Trip stub exists for your `trip_ids` One2many.

## IMPLEMENTATION NOTES / GOTCHAS
- `is_license_valid` must stay non-stored; the authoritative expiry check lives in D3's `action_dispatch` comparing dates — your compute is UI sugar.
- Odoo 18 view syntax rules as in `00` §8.
- When testing role users, remember menus hide when a user lacks ACL read on the action's model — a "missing menu" is usually a CSV row question for the Lead, not a view bug.
- Buttons on multiple statuses: get the `invisible` expressions from `04`'s wiring table exactly.

## WORKFLOW LOOP / SELF-QA / GIT
Same loop as all devs (`07` describes it; `20` teaches it): plan → edit own files → human upgrades module → click test → small commit (`feat(driver): BR-03 lifecycle actions`). Branch `feat/d2-drivers` only; pull `main` after each announced merge.
Self-QA slice: upgrade clean · duplicate license blocked (E-11) · safety score 101 blocked (E-13) · expired-license driver shows invalid toggle + appears under "License Expired" filter · suspend/off-duty flows + button visibility per state · suspend while on_trip blocked · RBAC matrix spot-check as SO and FA.

## STATUS OUTPUT / ESCALATION
Checkpoint status via `docs/17` template. Blocked >10 min or contract friction → surface immediately, never improvise.
