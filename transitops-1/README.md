# TransitOps Addon

TransitOps is an Odoo 18-compatible addon designed to manage trip workflows efficiently. This addon focuses on the `transitops.trip` model, providing essential functionalities for trip management, including CRUD operations, state management, and business rule enforcement.

## Project Structure

The project consists of the following files and directories:

- **transitops/__init__.py**: Initializes the models for the TransitOps addon.
- **transitops/__manifest__.py**: Contains metadata for the TransitOps addon, including name, version, author, and dependencies.
- **transitops/models/__init__.py**: Initializes the models directory and imports the trip model.
- **transitops/models/trip.py**: Defines the `transitops.trip` model with fields and methods for trip management.
- **transitops/views/trip_views.xml**: Defines views for the `transitops.trip` model, including actions, menus, and forms.
- **transitops/tests/__init__.py**: Initializes the tests directory for the TransitOps addon.
- **transitops/tests/test_business_rules.py**: Contains unit tests for the business rules of the `transitops.trip` model.

## Installation

To install the TransitOps addon, follow these steps:

1. Place the `transitops` directory in your Odoo addons path.
2. Update the app list in Odoo.
3. Search for "TransitOps" in the apps menu and click "Install".

## Usage

Once installed, you can access the trip management features under the Operations menu. You can create, view, and manage trips, including dispatching, completing, and canceling trips. The system enforces business rules to ensure data integrity and compliance with operational standards.

## Contributing

Contributions to the TransitOps addon are welcome. Please follow the standard Odoo development practices and ensure that your code adheres to the project's specifications.

## License

This project is licensed under the terms of the Odoo license. Please refer to the license file for more details.