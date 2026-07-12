# transitops/tests/test_business_rules.py

from odoo.tests import TransactionCase

class TestTripBusinessRules(TransactionCase):

    def setUp(self):
        super(TestTripBusinessRules, self).setUp()
        self.Vehicle = self.env['transitops.vehicle']
        self.Driver = self.env['transitops.driver']
        self.Trip = self.env['transitops.trip']
        
        # Create test vehicle and driver
        self.vehicle = self.Vehicle.create({
            'name': 'Test Vehicle',
            'max_load_kg': 1000,
            'status': 'available',
        })
        
        self.driver = self.Driver.create({
            'name': 'Test Driver',
            'status': 'available',
        })

    def test_cargo_weight_validation(self):
        # Test case for cargo weight exceeding vehicle capacity
        with self.assertRaises(Exception):
            self.Trip.create({
                'name': 'Test Trip',
                'vehicle_id': self.vehicle.id,
                'driver_id': self.driver.id,
                'cargo_weight_kg': 1500,  # Exceeds max load
                'planned_distance_km': 100,
            })

    def test_dispatch_trip(self):
        # Test dispatching a trip
        trip = self.Trip.create({
            'name': 'Test Trip',
            'vehicle_id': self.vehicle.id,
            'driver_id': self.driver.id,
            'cargo_weight_kg': 500,
            'planned_distance_km': 100,
        })
        trip.action_dispatch()
        self.assertEqual(trip.state, 'dispatched')

    def test_complete_trip(self):
        # Test completing a trip
        trip = self.Trip.create({
            'name': 'Test Trip',
            'vehicle_id': self.vehicle.id,
            'driver_id': self.driver.id,
            'cargo_weight_kg': 500,
            'planned_distance_km': 100,
        })
        trip.action_dispatch()
        trip.action_complete()
        self.assertEqual(trip.state, 'completed')

    def test_cancel_trip(self):
        # Test canceling a trip
        trip = self.Trip.create({
            'name': 'Test Trip',
            'vehicle_id': self.vehicle.id,
            'driver_id': self.driver.id,
            'cargo_weight_kg': 500,
            'planned_distance_km': 100,
        })
        trip.action_cancel()
        self.assertEqual(trip.state, 'canceled')