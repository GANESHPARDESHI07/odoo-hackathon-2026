from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class Trip(models.Model):
    _name = 'transitops.trip'
    _description = 'Trip Management'

    name = fields.Char(string='Trip Name', required=True, default='New', readonly=True, copy=False)
    source = fields.Char(string='Source', required=True)
    destination = fields.Char(string='Destination', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True)
    driver_id = fields.Many2one('res.users', string='Driver', required=True)
    cargo_weight_kg = fields.Float(string='Cargo Weight (kg)', required=True)
    planned_distance_km = fields.Float(string='Planned Distance (km)', required=True)
    revenue = fields.Float(string='Revenue', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('dispatched', 'Dispatched'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ], default='draft', string='Status', tracking=True)
    dispatch_datetime = fields.Datetime(string='Dispatch Date & Time', readonly=True)
    complete_datetime = fields.Datetime(string='Completion Date & Time', readonly=True)
    start_odometer_km = fields.Float(string='Start Odometer (km)', readonly=True)
    end_odometer_km = fields.Float(string='End Odometer (km)')
    actual_distance_km = fields.Float(string='Actual Distance (km)', compute='_compute_actual_distance', store=True)
    fuel_consumed_l = fields.Float(string='Fuel Consumed (L)')
    fuel_cost = fields.Float(string='Fuel Cost')
    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('transitops.trip') or 'New'
        return super(Trip, self).create(vals)

    def unlink(self):
        for trip in self:
            if trip.state != 'draft':
                raise UserError('Only draft trips can be deleted.')
        return super(Trip, self).unlink()

    @api.constrains('cargo_weight_kg')
    def _check_cargo_weight(self):
        for record in self:
            if record.cargo_weight_kg <= 0:
                raise ValidationError("Cargo weight must be positive.")
            if record.cargo_weight_kg > record.vehicle_id.max_load_kg:
                raise ValidationError(
                    f"Cargo weight ({record.cargo_weight_kg} kg) exceeds the maximum load capacity of {record.vehicle_id.name} ({record.vehicle_id.max_load_kg} kg)."
                )

    @api.depends('start_odometer_km', 'end_odometer_km', 'state')
    def _compute_actual_distance(self):
        for record in self:
            if record.state == 'completed':
                record.actual_distance_km = max(record.end_odometer_km - record.start_odometer_km, 0.0)
            else:
                record.actual_distance_km = 0.0

    def action_dispatch(self):
        for trip in self:
            if trip.state != 'draft':
                raise UserError('Only draft trips can be dispatched.')
            if trip.vehicle_id.status != 'available':
                raise UserError(f"Vehicle {trip.vehicle_id.name} is not available for dispatch (current status: {trip.vehicle_id.status}).")
            if trip.driver_id.status != 'available':
                raise UserError(f"Driver {trip.driver_id.name} is not available for dispatch (current status: {trip.driver_id.status}).")
            if trip.driver_id.license_expiry < fields.Date.context_today(self):
                raise UserError(f"Driver {trip.driver_id.name}'s license expired on {trip.driver_id.license_expiry}. Assignment blocked.")
            trip.start_odometer_km = trip.vehicle_id.odometer_km
            trip.dispatch_datetime = fields.Datetime.now()
            trip.state = 'dispatched'
            trip.vehicle_id.status = 'on_trip'
            trip.driver_id.status = 'on_trip'

    def action_complete(self):
        for trip in self:
            if trip.state != 'dispatched':
                raise UserError('Only dispatched trips can be completed.')
            if not trip.end_odometer_km:
                raise UserError('Enter the end odometer reading before completing the trip.')
            if trip.end_odometer_km < trip.start_odometer_km:
                raise UserError(f"End odometer ({trip.end_odometer_km} km) cannot be less than start odometer ({trip.start_odometer_km} km).")
            trip.vehicle_id.odometer_km = trip.end_odometer_km
            trip.complete_datetime = fields.Datetime.now()
            trip.state = 'completed'
            trip.vehicle_id.status = 'available'
            trip.driver_id.status = 'available'
            if trip.fuel_consumed_l > 0:
                self.env['transitops.fuel.log'].create({
                    'vehicle_id': trip.vehicle_id.id,
                    'trip_id': trip.id,
                    'date': fields.Date.context_today(self),
                    'liters': trip.fuel_consumed_l,
                    'cost': trip.fuel_cost or 0.0,
                    'odometer_km': trip.end_odometer_km,
                    'source': 'trip',
                })

    def action_cancel(self):
        for trip in self:
            if trip.state == 'completed':
                raise UserError('Completed trips cannot be cancelled.')
            if trip.state == 'dispatched':
                trip.vehicle_id.status = 'available'
                trip.driver_id.status = 'available'
            trip.state = 'canceled'