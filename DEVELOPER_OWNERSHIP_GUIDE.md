# TransitOps Developer Ownership Guide

> Defines ownership boundaries for the 4-person team.

## Developer 1 --- Authentication, RBAC & Dashboard

### Owns

-   security/
-   dashboard/
-   authentication/

### Responsibilities

-   Login & Authentication
-   RBAC
-   Dashboard UI
-   KPI cards
-   Dashboard charts
-   Navigation & menu visibility
-   Security groups
-   ACLs & Record Rules

### Do NOT Modify

-   Vehicles
-   Drivers
-   Trips
-   Maintenance
-   Fuel & Expenses
-   Reports

------------------------------------------------------------------------

## Developer 2 --- Fleet Management

### Owns

-   models/vehicle.py
-   models/driver.py
-   models/maintenance.py
-   Vehicle/Driver/Maintenance views

### Responsibilities

-   Vehicle CRUD
-   Driver CRUD
-   Maintenance CRUD
-   Validations
-   Maintenance workflow

### Do NOT Modify

-   Trip workflow
-   Reports
-   Dashboard business logic

------------------------------------------------------------------------

## Developer 3 --- Trips & Dispatch

### Owns

-   models/trip.py
-   dispatch/
-   rule_engine/
-   Trip views

### Responsibilities

-   Trip lifecycle
-   Dispatch
-   Complete
-   Cancel
-   Business rules
-   Cargo validation
-   Double-book prevention
-   Status automation

### Do NOT Modify

-   Vehicle CRUD
-   Driver CRUD
-   Maintenance CRUD
-   Reports

------------------------------------------------------------------------

## Developer 4 --- Finance & Analytics

### Owns

-   models/fuel.py
-   models/expense.py
-   reports/
-   analytics/

### Responsibilities

-   Fuel Logs
-   Expenses
-   ROI
-   Fuel Efficiency
-   Operational Cost
-   Reports
-   Charts
-   CSV/PDF Export

### Do NOT Modify

-   Authentication
-   Trip workflow
-   Vehicle/Driver CRUD

------------------------------------------------------------------------

## Shared Files

Only modify after team coordination:

-   **manifest**.py
-   **init**.py
-   models/**init**.py
-   security/ir.model.access.csv
-   views/menus.xml

------------------------------------------------------------------------

## Integration Lead

-   Merge feature branches
-   Resolve merge conflicts
-   Test end-to-end workflow
-   Verify business rules
-   Prepare final demo

------------------------------------------------------------------------

## Branches

-   feature/auth-dashboard
-   feature/fleet
-   feature/trips
-   feature/analytics

Only the Integration Lead merges into `main`.
