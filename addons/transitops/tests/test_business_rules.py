from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError


class TestBusinessRules(TransactionCase):
    def setUp(self):
        super().setUp()
        self.vehicle = self.env['transitops.vehicle'].create({
            'name': 'Test Van', 'registration_no': 'MH12TEST', 'vehicle_type': 'van',
            'max_load_kg': 500, 'odometer_km': 1000})
        self.driver = self.env['transitops.driver'].create({
            'name': 'Test Driver', 'license_no': 'LIC-TEST',
            'license_category': 'lmv', 'license_expiry': '2030-01-01'})

    def test_cargo_overweight_blocked(self):
        with self.assertRaises(ValidationError):
            self.env['transitops.trip'].create({'source': 'A', 'destination': 'B',
                'vehicle_id': self.vehicle.id, 'driver_id': self.driver.id,
                'cargo_weight_kg': 600})

    def test_dispatch_flips_statuses(self):
        trip = self.env['transitops.trip'].create({'source': 'A', 'destination': 'B',
            'vehicle_id': self.vehicle.id, 'driver_id': self.driver.id,
            'cargo_weight_kg': 400})
        trip.action_dispatch()
        self.vehicle.refresh()
        self.driver.refresh()
        self.assertEqual(self.vehicle.status, 'on_trip')
        self.assertEqual(self.driver.status, 'on_trip')

    def test_complete_restores_and_updates_odometer(self):
        trip = self.env['transitops.trip'].create({'source': 'A', 'destination': 'B',
            'vehicle_id': self.vehicle.id, 'driver_id': self.driver.id,
            'cargo_weight_kg': 400})
        trip.action_dispatch()
        trip.end_odometer_km = 1150
        trip.fuel_consumed_l = 15
        trip.fuel_cost = 1500
        trip.action_complete()
        self.vehicle.refresh()
        self.assertEqual(self.vehicle.status, 'available')
        self.assertEqual(self.vehicle.odometer_km, 1150)
        self.assertEqual(trip.actual_distance_km, 150)
