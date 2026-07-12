# 11 — INTEGRATION LEAD PLAYBOOK (Developer 1 wears this hat)

You own: the Hour-0 skeleton, all frozen files, every merge, the health of `main`, contract arbitration, final QA coordination, README and submission. Your Claude Code session for Lead work is SEPARATE from your D1 dev session (different concern, keep contexts clean — `/clear` between hats).

---

## 1. HOUR 0 — SKELETON (target: committed & pushed by 0:25)

Create the structure, paste the frozen files below verbatim, then generate stubs (§1.9). Commit as `chore: hour-0 skeleton — all contracts frozen`, push `main`, create the four feature branches, announce "SKELETON UP — everyone pull and install."

### 1.1 `addons/transitops/__init__.py`
```python
from . import models
```

### 1.2 `addons/transitops/__manifest__.py`  (FROZEN)
```python
{
    "name": "TransitOps",
    "summary": "Smart Transport Operations Platform — fleet, drivers, trips, maintenance, fuel & analytics",
    "version": "18.0.1.0.0",
    "category": "Operations/Fleet",
    "author": "Team TransitOps",
    "license": "LGPL-3",
    "depends": ["base", "mail", "web"],
    "data": [
        "security/security_groups.xml",
        "security/ir.model.access.csv",
        "security/record_rules.xml",
        "data/ir_sequence.xml",
        "views/menus.xml",
        "views/vehicle_views.xml",
        "views/maintenance_views.xml",
        "views/driver_views.xml",
        "views/trip_views.xml",
        "views/fuel_expense_views.xml",
        "views/dashboard_views.xml",
    ],
    "demo": ["demo/demo_data.xml"],
    "assets": {
        "web.assets_backend": [
            "transitops/static/src/dashboard/**/*",
        ],
    },
    "application": True,
    "installable": True,
}
```

### 1.3 `addons/transitops/models/__init__.py`  (FROZEN)
```python
from . import vehicle
from . import driver
from . import trip
from . import maintenance
from . import fuel_log
from . import expense
```

### 1.4 `security/security_groups.xml`  (FROZEN)
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="module_category_transitops" model="ir.module.category">
        <field name="name">TransitOps</field>
        <field name="sequence">25</field>
    </record>
    <record id="group_transitops_fleet_manager" model="res.groups">
        <field name="name">Fleet Manager</field>
        <field name="category_id" ref="module_category_transitops"/>
    </record>
    <record id="group_transitops_dispatcher" model="res.groups">
        <field name="name">Dispatcher</field>
        <field name="category_id" ref="module_category_transitops"/>
    </record>
    <record id="group_transitops_safety_officer" model="res.groups">
        <field name="name">Safety Officer</field>
        <field name="category_id" ref="module_category_transitops"/>
    </record>
    <record id="group_transitops_analyst" model="res.groups">
        <field name="name">Financial Analyst</field>
        <field name="category_id" ref="module_category_transitops"/>
    </record>
</odoo>
```

### 1.5 `security/ir.model.access.csv`  (FROZEN — implements `00` §10)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_vehicle_fm,vehicle fm,model_transitops_vehicle,group_transitops_fleet_manager,1,1,1,1
access_vehicle_dp,vehicle dp,model_transitops_vehicle,group_transitops_dispatcher,1,0,0,0
access_vehicle_so,vehicle so,model_transitops_vehicle,group_transitops_safety_officer,1,0,0,0
access_vehicle_fa,vehicle fa,model_transitops_vehicle,group_transitops_analyst,1,0,0,0
access_driver_fm,driver fm,model_transitops_driver,group_transitops_fleet_manager,1,0,0,0
access_driver_dp,driver dp,model_transitops_driver,group_transitops_dispatcher,1,0,0,0
access_driver_so,driver so,model_transitops_driver,group_transitops_safety_officer,1,1,1,1
access_driver_fa,driver fa,model_transitops_driver,group_transitops_analyst,1,0,0,0
access_trip_fm,trip fm,model_transitops_trip,group_transitops_fleet_manager,1,1,0,0
access_trip_dp,trip dp,model_transitops_trip,group_transitops_dispatcher,1,1,1,1
access_trip_so,trip so,model_transitops_trip,group_transitops_safety_officer,1,0,0,0
access_trip_fa,trip fa,model_transitops_trip,group_transitops_analyst,1,0,0,0
access_maintenance_fm,maintenance fm,model_transitops_maintenance,group_transitops_fleet_manager,1,1,1,1
access_maintenance_dp,maintenance dp,model_transitops_maintenance,group_transitops_dispatcher,1,0,0,0
access_maintenance_so,maintenance so,model_transitops_maintenance,group_transitops_safety_officer,1,0,0,0
access_maintenance_fa,maintenance fa,model_transitops_maintenance,group_transitops_analyst,1,0,0,0
access_fuel_fm,fuel fm,model_transitops_fuel_log,group_transitops_fleet_manager,1,1,1,0
access_fuel_dp,fuel dp,model_transitops_fuel_log,group_transitops_dispatcher,1,1,1,0
access_fuel_so,fuel so,model_transitops_fuel_log,group_transitops_safety_officer,1,0,0,0
access_fuel_fa,fuel fa,model_transitops_fuel_log,group_transitops_analyst,1,0,0,0
access_expense_fm,expense fm,model_transitops_expense,group_transitops_fleet_manager,1,1,1,0
access_expense_dp,expense dp,model_transitops_expense,group_transitops_dispatcher,1,1,1,0
access_expense_so,expense so,model_transitops_expense,group_transitops_safety_officer,1,0,0,0
access_expense_fa,expense fa,model_transitops_expense,group_transitops_analyst,1,0,0,0
access_vehicle_sys,vehicle sys,model_transitops_vehicle,base.group_system,1,1,1,1
access_driver_sys,driver sys,model_transitops_driver,base.group_system,1,1,1,1
access_trip_sys,trip sys,model_transitops_trip,base.group_system,1,1,1,1
access_maintenance_sys,maintenance sys,model_transitops_maintenance,base.group_system,1,1,1,1
access_fuel_sys,fuel sys,model_transitops_fuel_log,base.group_system,1,1,1,1
access_expense_sys,expense sys,model_transitops_expense,base.group_system,1,1,1,1
```

### 1.6 `security/record_rules.xml` (stub) and `data/ir_sequence.xml` (FROZEN)
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo/>
```
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="seq_transitops_trip" model="ir.sequence">
        <field name="name">TransitOps Trip</field>
        <field name="code">transitops.trip</field>
        <field name="prefix">TRIP/%(year)s/</field>
        <field name="padding">4</field>
    </record>
</odoo>
```

### 1.7 `views/menus.xml`  (FROZEN — roots/sections only; loaded first)
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <menuitem id="menu_transitops_root" name="TransitOps" sequence="10" web_icon="transitops,static/description/icon.png"/>
    <menuitem id="menu_transitops_operations" name="Operations" parent="menu_transitops_root" sequence="10"/>
    <menuitem id="menu_transitops_fleet" name="Fleet" parent="menu_transitops_root" sequence="20"/>
    <menuitem id="menu_transitops_drivers" name="Drivers" parent="menu_transitops_root" sequence="30"/>
    <menuitem id="menu_transitops_finance" name="Finance" parent="menu_transitops_root" sequence="40"/>
    <menuitem id="menu_transitops_reporting" name="Reporting" parent="menu_transitops_root" sequence="50"/>
</odoo>
```
(If no icon file exists, drop the `web_icon` attribute — do not let it block install.)

### 1.8 Dashboard stub (working from Hour 0; D4 extends)

`views/dashboard_views.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="action_transitops_dashboard" model="ir.actions.client">
        <field name="name">Dashboard</field>
        <field name="tag">transitops.dashboard</field>
    </record>
    <menuitem id="menu_transitops_dashboard" name="Dashboard" parent="menu_transitops_root"
              action="action_transitops_dashboard" sequence="1"/>
</odoo>
```
`static/src/dashboard/dashboard.js`:
```javascript
/** @odoo-module **/
import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class TransitOpsDashboard extends Component {
    static template = "transitops.Dashboard";
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ k: {}, loading: true });
        onWillStart(() => this.load());
    }
    async load() {
        const V = "transitops.vehicle", T = "transitops.trip", D = "transitops.driver";
        const c = (m, d) => this.orm.searchCount(m, d);
        const [fleet, avail, shop, ontrip, active, pending, onduty] = await Promise.all([
            c(V, [["status", "!=", "retired"]]), c(V, [["status", "=", "available"]]),
            c(V, [["status", "=", "in_shop"]]), c(V, [["status", "=", "on_trip"]]),
            c(T, [["state", "=", "dispatched"]]), c(T, [["state", "=", "draft"]]),
            c(D, [["status", "in", ["available", "on_trip"]]]),
        ]);
        const util = fleet ? Math.round((ontrip / fleet) * 1000) / 10 : 0;
        this.state.k = { fleet, avail, shop, ontrip, active, pending, onduty, util };
        this.state.loading = false;
    }
    open(model, domain, name) {
        this.action.doAction({ type: "ir.actions.act_window", res_model: model, name,
            views: [[false, "list"], [false, "form"]], domain });
    }
}
registry.category("actions").add("transitops.dashboard", TransitOpsDashboard);
```
`static/src/dashboard/dashboard.xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
<t t-name="transitops.Dashboard">
    <div class="o_transitops_dashboard p-4">
        <h2 class="mb-4">TransitOps — Fleet Overview</h2>
        <div t-if="state.loading">Loading…</div>
        <div t-else="" class="row g-3">
            <div class="col-6 col-md-3"><div class="o_to_card" t-on-click="() => this.open('transitops.vehicle', [['status','!=','retired']], 'Fleet')">
                <div class="o_to_num" t-esc="state.k.fleet"/><div>Total Fleet</div></div></div>
            <div class="col-6 col-md-3"><div class="o_to_card" t-on-click="() => this.open('transitops.vehicle', [['status','=','available']], 'Available')">
                <div class="o_to_num" t-esc="state.k.avail"/><div>Available Vehicles</div></div></div>
            <div class="col-6 col-md-3"><div class="o_to_card" t-on-click="() => this.open('transitops.vehicle', [['status','=','in_shop']], 'In Maintenance')">
                <div class="o_to_num" t-esc="state.k.shop"/><div>In Maintenance</div></div></div>
            <div class="col-6 col-md-3"><div class="o_to_card" t-on-click="() => this.open('transitops.vehicle', [['status','=','on_trip']], 'On Trip')">
                <div class="o_to_num" t-esc="state.k.ontrip"/><div>On Trip</div></div></div>
            <div class="col-6 col-md-3"><div class="o_to_card" t-on-click="() => this.open('transitops.trip', [['state','=','dispatched']], 'Active Trips')">
                <div class="o_to_num" t-esc="state.k.active"/><div>Active Trips</div></div></div>
            <div class="col-6 col-md-3"><div class="o_to_card" t-on-click="() => this.open('transitops.trip', [['state','=','draft']], 'Pending Trips')">
                <div class="o_to_num" t-esc="state.k.pending"/><div>Pending Trips</div></div></div>
            <div class="col-6 col-md-3"><div class="o_to_card" t-on-click="() => this.open('transitops.driver', [['status','in',['available','on_trip']]], 'On Duty')">
                <div class="o_to_num" t-esc="state.k.onduty"/><div>Drivers On Duty</div></div></div>
            <div class="col-6 col-md-3"><div class="o_to_card">
                <div class="o_to_num"><t t-esc="state.k.util"/>%</div><div>Fleet Utilization</div></div></div>
        </div>
    </div>
</t>
</templates>
```
`static/src/dashboard/dashboard.scss`:
```scss
.o_transitops_dashboard .o_to_card {
    background: var(--o-view-background-color, #fff);
    border: 1px solid #dee2e6; border-radius: 8px; padding: 16px;
    text-align: center; cursor: pointer; transition: box-shadow .15s;
    &:hover { box-shadow: 0 2px 8px rgba(0,0,0,.12); }
    .o_to_num { font-size: 2rem; font-weight: 700; }
}
```

### 1.9 Model & view stubs — generate with Claude Code
Prompt (verbatim): *"Read docs/02_DATABASE_CONTRACT.md. Create the six model files listed in docs/00 §3 under addons/transitops/models/, each containing the class with `_name`, `_description`, `_inherit`/`_order` and EVERY field defined exactly as in 02 (all params: selection keys, defaults, required, tracking, index, related, compute stubs returning/setting 0). Compute methods may be minimal stubs; action methods may `return True`. No views, no constraints yet. Also create views/vehicle_views.xml, maintenance_views.xml, driver_views.xml, trip_views.xml, fuel_expense_views.xml each as an empty `<odoo/>` document, and tests/__init__.py empty. Then stop."*
Verify: `odoo-bin -d transitops_skel -i transitops --stop-after-init` exits clean; open the UI, root menu + Dashboard stub render. Delete the throwaway db if you like; commit; branch:
```bash
git checkout -b feat/d1-fleet && git push -u origin feat/d1-fleet   # repeat for d2/d3/d4
```

## 2. MERGE PROCEDURE (checkpoints 2:15, 4:45, 6:15)
1. Announce `MERGE WINDOW OPEN — freeze pushes`. Collect `17` statuses + `18` merge notes.
2. On a clean tree: `git checkout main && git pull`.
3. Merge in order d1→d2→d3→d4: `git merge --no-ff feat/d1-fleet`. Conflicts should be ~zero; if any: owner of the file decides, frozen file conflict = Lead's version wins.
4. After EACH merge: `odoo-bin -d transitops_ci -u transitops --stop-after-init` (create `transitops_ci` once with `-i`). Traceback → the just-merged dev fixes on their branch within 10 min, re-merge; if not fixable fast, `git reset --hard` to pre-merge tag and continue with the others (see `21` §4).
5. After all four: smoke-run the spec §5 example workflow (Merge 2 onward) + one RBAC login. Tag `v0.1` / `v0.2` / `v1.0-rc`. Announce `MERGED — everyone: git checkout your-branch && git merge main`.

## 3. CONTRACT ARBITRATION
You are the only person who edits frozen files, always on `main` directly, always announced as `CONTRACT vN: <change>`. Default answer to mid-hackathon contract changes is **no** unless a mandatory deliverable is blocked.

## 4. HOUR 7 — SUBMISSION PACKAGE
Fresh final db `transitops_demo` created **with demo data**; run full `12` regression; write repo `README.md` (template: project name & one-liner, problem→solution paragraph, feature list mapped to spec's mandatory deliverables + claimed bonuses, tech stack, setup commands, demo credentials table, team members, architecture diagram from `01`); fill `19_QUALITY_REPORT`; screenshots (dashboard, trip form, blocked-dispatch error); push, tag `v1.0`, submit per organizer instructions; then run the demo rehearsal from `15`.

## 5. YOUR TIME BUDGET
Hour 0 skeleton ≈ 30 min; each merge window ≈ 30 min; Hour 7 ≈ 45 min. Everything else you're Developer 1 — protect that time by refusing scope creep fast.
