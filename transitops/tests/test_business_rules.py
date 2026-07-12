from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError


class TestTransitOpsTrip(TransactionCase):

    def setUp(self):
        super().setUp()
        self.vehicle = self.env['fleet.vehicle'].create({
            'name': 'Truck 1',
            'status': 'available',
            'max_load_kg': 500,
            'odometer_km': 1000,
        })
        self.driver = self.env['res.users'].create({
            'name': 'Driver 1',
            'status': 'available',
            'license_expiry': '2099-12-31',
        })

    def test_cargo_overweight_blocked(self):
        with self.assertRaises(ValidationError):
            self.env['transitops.trip'].create({
                'source': 'A',
                'destination': 'B',
                'vehicle_id': self.vehicle.id,
                'driver_id': self.driver.id,
                'cargo_weight_kg': 600,
            })

    def test_dispatch_flips_statuses(self):
        trip = self.env['transitops.trip'].create({
            'source': 'A',
            'destination': 'B',
            'vehicle_id': self.vehicle.id,
            'driver_id': self.driver.id,
            'cargo_weight_kg': 400,
        })
        trip.action_dispatch()
        self.assertEqual(trip.vehicle_id.status, 'on_trip')
        self.assertEqual(trip.driver_id.status, 'on_trip')

    def test_complete_restores_and_updates_odometer(self):
        trip = self.env['transitops.trip'].create({
            'source': 'A',
            'destination': 'B',
            'vehicle_id': self.vehicle.id,
            'driver_id': self.driver.id,
            'cargo_weight_kg': 400,
        })
        trip.action_dispatch()
        trip.end_odometer_km = 1150
        trip.fuel_consumed_l = 50
        trip.fuel_cost = 100
        trip.action_complete()
        self.assertEqual(trip.vehicle_id.status, 'available')
        self.assertEqual(trip.vehicle_id.odometer_km, 1150)
        self.assertEqual(trip.actual_distance_km, 150)