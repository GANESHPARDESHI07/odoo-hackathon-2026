from odoo import models, fields, api, exceptions

class Trip(models.Model):
    _name = 'transitops.trip'
    _description = 'Trip Management'

    name = fields.Char(string='Trip Name', required=True)
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
    ], default='draft', string='Status')
    dispatch_datetime = fields.Datetime(string='Dispatch Date & Time')
    complete_datetime = fields.Datetime(string='Completion Date & Time')
    start_odometer_km = fields.Float(string='Start Odometer (km)')
    end_odometer_km = fields.Float(string='End Odometer (km)')
    actual_distance_km = fields.Float(string='Actual Distance (km)', compute='_compute_actual_distance', store=True)
    fuel_consumed_l = fields.Float(string='Fuel Consumed (L)')
    fuel_cost = fields.Float(string='Fuel Cost')
    notes = fields.Text(string='Notes')

    @api.constrains('cargo_weight_kg')
    def _check_cargo_weight(self):
        for record in self:
            if record.cargo_weight_kg <= 0:
                raise exceptions.ValidationError("Cargo weight must be positive.")

    @api.model
    def create(self, vals):
        # Override create method to set default values if necessary
        return super(Trip, self).create(vals)

    def unlink(self):
        # Override unlink method to add any necessary logic before deletion
        return super(Trip, self).unlink()

    def action_dispatch(self):
        self.state = 'dispatched'
        self.dispatch_datetime = fields.Datetime.now()

    def action_complete(self):
        self.state = 'completed'
        self.complete_datetime = fields.Datetime.now()

    def action_cancel(self):
        self.state = 'canceled'

    @api.depends('start_odometer_km', 'end_odometer_km')
    def _compute_actual_distance(self):
        for record in self:
            record.actual_distance_km = record.end_odometer_km - record.start_odometer_km if record.end_odometer_km and record.start_odometer_km else 0.0