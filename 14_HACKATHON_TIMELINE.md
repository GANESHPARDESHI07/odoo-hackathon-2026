# 14 — HACKATHON TIMELINE (8:00:00 on the clock)

Pre-hackathon homework (night before, 45 min/person): environment installed & Odoo boots; kit read (own file + `00` + `16`); Claude Code authenticated; repo cloned. **Hour 0 assumes this is done.**

Legend: ✅ = hard checkpoint gate (if red, `21` applies immediately).

## 0:00 – 0:30 · BOOT
| Who | Doing |
|---|---|
| All (0:00–0:10) | Standup: confirm Odoo version in `00` §1 · reconcile mockup deltas into `05` · confirm roles · start a shared timer |
| Lead | Execute `11` §1: skeleton, frozen files, stubs, push, branches (target 0:25) |
| D2, D3, D4 | Odoo server running on local db; Claude Code session opened with `CLAUDE.md` + own dev file loaded; read while waiting |
| All (0:25–0:30) | Pull `main`, `-i transitops` locally ✅ **Gate A: module installs on all 4 machines, root menu + dashboard stub visible** |

## 0:30 – 2:15 · SPRINT 1 — models + basic UI (details in each dev file §Sprint 1)
| Who | Deliverable by 2:15 |
|---|---|
| D1 | Vehicle + Maintenance models complete, CRUD views, menus, E-01/E-08/E-12 live |
| D2 | Driver model complete, views, License-Expired filter, RBAC matrix verified |
| D3 | Trip model + sequence + cargo constraint + views with domains + BR-13 |
| D4 | Fuel/Expense models+views, dashboard 8 cards live, seed data v1 (users, vehicles, drivers) |
| 1:15 | Mid-sprint pulse: one-line status each in chat; blockers surfaced |

## 2:15 – 2:45 · MERGE 1 (Lead runs `11` §2) ✅ **Gate B: main installs with all models & menus; v0.1 tagged**
Others during window: run own Self-QA slice; no pushes. After: everyone merges `main` into their branch.

## 2:45 – 4:45 · SPRINT 2 — business logic (the scoring sprint)
| Who | Deliverable by 4:45 |
|---|---|
| D1 | action_retire, maintenance close/cancel + release logic, all financial computes |
| D2 | Four driver lifecycle actions + button visibility/groups; joint license-block test with D3 |
| D3 | Dispatch/Complete/Cancel fully per `04` incl. fuel-log auto-create; example workflow passes locally |
| D4 | Card click-throughs, dashboard filters, seed data v2 (completed trips/fuel/expenses), reporting pivots |
| 3:45 | Pulse check |

## 4:45 – 5:15 · MERGE 2 ✅ **Gate C: spec §5 example workflow passes end-to-end on main; v0.2 tagged**
All-hands smoke test (Lead drives, screen-shared): register → dispatch → block-overweight → complete → maintenance → dashboard moves. Integration bugs fixed NOW by owners (this half hour exists for exactly that).

## 5:15 – 6:15 · SPRINT 3 — polish & pre-approved stretch only (`00` §11)
| Who | Priority order (stop when time's up) |
|---|---|
| D1 | Decorations/help-text audit → vehicle kanban → chatter niceties |
| D2 | RBAC demo rehearsal (role switch) → license cron OR record rules (pick one) |
| D3 | Edge hardening from `12` §C → automated tests (Appendix A) |
| D4 | KPI math hand-verification vs seed → dashboard polish → QWeb PDF (only if everything green) |

## 6:15 – 6:45 · MERGE 3 = **FEATURE FREEZE** ✅ **Gate D: v1.0-rc tagged; hotfix-only mode begins (`13` §8)**

## 6:45 – 7:30 · FULL QA (all hands, split the `12` matrix: D1→A+D, D2→B+G, D3→C, D4→E+F+H)
Lead creates the final `transitops_demo` db with demo data; bugs triaged: demo-path bugs fixed via hotfix, cosmetic bugs logged in `19` as known issues and left alone.

## 7:30 – 8:00 · SHIP
| Min | Doing |
|---|---|
| 7:30–7:45 | Demo rehearsal ×2 on final db (presenter + backup presenter), timed |
| 7:40–7:55 | Lead in parallel: README, `19_QUALITY_REPORT`, screenshots, tag `v1.0`, **submit** (submit at 7:50, not 7:59) |
| 7:55–8:00 | Buffer. Nothing new. Breathe. |

## Standing rules all 8 hours
Blockers > 10 min → announce. Pulse checks are one line, not meetings. Scope requests outside your dev file → Lead decides in ≤2 min, default no. Falling >30 min behind sprint targets → open `21` §2 and shed scope per your listed cut order — nobody hero-codes silently.
