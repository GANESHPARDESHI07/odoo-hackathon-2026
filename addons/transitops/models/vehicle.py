from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class TransitopsVehicle(models.Model):
    _name = 'transitops.vehicle'
    _description = 'Vehicle'
    _inherit = ['mail.thread']
    _order = 'name'
    _rec_names_search = ['name', 'registration_no']

    name = fields.Char(required=True)
    registration_no = fields.Char(required=True, index=True, copy=False)
    vehicle_type = fields.Selection(
        [('truck', 'Truck'), ('van', 'Van'), ('bus', 'Bus'), ('car', 'Car'), ('bike', 'Bike')],
        required=True,
        default='van',
        tracking=True,
    )
    region = fields.Selection(
        [('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West'), ('central', 'Central')],
        default='west',
        tracking=True,
    )
    max_load_kg = fields.Float(required=True)
    odometer_km = fields.Float(default=0.0, tracking=True)
    acquisition_cost = fields.Float(default=0.0)
    status = fields.Selection(
        [('available', 'Available'), ('on_trip', 'On Trip'), ('in_shop', 'In Shop'), ('retired', 'Retired')],
        default='available',
        required=True,
        index=True,
        tracking=True,
    )
    notes = fields.Text()
    active = fields.Boolean(default=True)

    trip_ids = fields.One2many('transitops.trip', 'vehicle_id')
    maintenance_ids = fields.One2many('transitops.maintenance', 'vehicle_id')
    fuel_log_ids = fields.One2many('transitops.fuel.log', 'vehicle_id')
    expense_ids = fields.One2many('transitops.expense', 'vehicle_id')

    total_fuel_cost = fields.Float(compute='_compute_financials', store=True)
    total_fuel_liters = fields.Float(compute='_compute_financials', store=True)
    total_maintenance_cost = fields.Float(compute='_compute_financials', store=True)
    total_operational_cost = fields.Float(compute='_compute_financials', store=True)
    total_expense_other = fields.Float(compute='_compute_financials', store=True)
    total_distance_km = fields.Float(compute='_compute_financials', store=True)
    total_revenue = fields.Float(compute='_compute_financials', store=True)
    fuel_efficiency_kmpl = fields.Float(compute='_compute_financials', store=True)
    roi_pct = fields.Float(compute='_compute_financials', store=True)

    _sql_constraints = [
        ('registration_unique', 'unique(registration_no)', _('A vehicle with this registration number already exists.')),
    ]

    @api.constrains('max_load_kg')
    def _check_max_load(self):
        # BR-12
        for record in self:
            if record.max_load_kg <= 0:
                raise ValidationError(_('Maximum load capacity must be greater than zero.'))

    @api.depends(
        'fuel_log_ids.cost',
        'fuel_log_ids.liters',
        'maintenance_ids.cost',
        'maintenance_ids.state',
        'trip_ids.state',
        'trip_ids.actual_distance_km',
        'trip_ids.revenue',
        'acquisition_cost',
    )
    def _compute_financials(self):
        # BR-14 / BR-15
        for record in self:
            total_fuel_cost = sum(record.fuel_log_ids.mapped('cost') or [0.0])
            total_fuel_liters = sum(record.fuel_log_ids.mapped('liters') or [0.0])
            maintenance_costs = record.maintenance_ids.filtered(lambda m: m.state != 'cancelled').mapped('cost')
            total_maintenance_cost = sum(maintenance_costs or [0.0])
            total_expense_other = sum(record.expense_ids.mapped('amount') or [0.0])
            completed_trips = record.trip_ids.filtered(lambda t: t.state == 'completed')
            total_distance_km = sum(completed_trips.mapped('actual_distance_km') or [0.0])
            total_revenue = sum(completed_trips.mapped('revenue') or [0.0])
            total_operational_cost = total_fuel_cost + total_maintenance_cost

            if total_fuel_liters:
                fuel_efficiency_kmpl = round(total_distance_km / total_fuel_liters, 2)
            else:
                fuel_efficiency_kmpl = 0.0

            if record.acquisition_cost:
                roi_pct = round(((total_revenue - total_operational_cost) / record.acquisition_cost) * 100.0, 1)
            else:
                roi_pct = 0.0

            record.total_fuel_cost = total_fuel_cost
            record.total_fuel_liters = total_fuel_liters
            record.total_maintenance_cost = total_maintenance_cost
            record.total_operational_cost = total_operational_cost
            record.total_expense_other = total_expense_other
            record.total_distance_km = total_distance_km
            record.total_revenue = total_revenue
            record.fuel_efficiency_kmpl = fuel_efficiency_kmpl
            record.roi_pct = roi_pct

    def action_retire(self):
        # BR-16
        for record in self:
            if record.status == 'on_trip':
                raise UserError(
                    _('Vehicle {vehicle} cannot be retired while On Trip.').format(
                        vehicle=record.name or record.registration_no
                    )
                )
            record.status = 'retired'
            record.message_post(body=_('Vehicle retired'))
        return True
