from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class TransitopsTrip(models.Model):
    _name = 'transitops.trip'
    _description = 'Trip'
    _inherit = ['mail.thread']
    _order = 'id desc'

    name = fields.Char(string='Reference', default='New', copy=False, readonly=True)
    source = fields.Char(required=True)
    destination = fields.Char(required=True)
    vehicle_id = fields.Many2one('transitops.vehicle', string='Vehicle', required=True, tracking=True)
    driver_id = fields.Many2one('transitops.driver', string='Driver', required=True, tracking=True)
    vehicle_max_load_kg = fields.Float(related='vehicle_id.max_load_kg', string='Vehicle Max Load')
    cargo_weight_kg = fields.Float(string='Cargo Weight (kg)', required=True)
    planned_distance_km = fields.Float(string='Planned Distance (km)')
    revenue = fields.Float(string='Revenue', default=0.0)
    state = fields.Selection([('draft','Draft'),('dispatched','Dispatched'),('completed','Completed'),('cancelled','Cancelled')],
                             string='State', default='draft', required=True, index=True, tracking=True)
    dispatch_datetime = fields.Datetime(string='Dispatch Date', readonly=True, copy=False)
    complete_datetime = fields.Datetime(string='Completion Date', readonly=True, copy=False)
    start_odometer_km = fields.Float(string='Start Odometer (km)', readonly=True, copy=False)
    end_odometer_km = fields.Float(string='End Odometer (km)', copy=False)
    actual_distance_km = fields.Float(string='Actual Distance (km)', compute='_compute_actual_distance', store=True)
    fuel_consumed_l = fields.Float(string='Fuel Consumed (L)')
    fuel_cost = fields.Float(string='Fuel Cost')
    notes = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        seq_obj = self.env['ir.sequence']
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'New':
                try:
                    vals['name'] = seq_obj.next_by_code('transitops.trip') or 'New'
                except Exception:
                    vals['name'] = 'New'
        return super().create(vals_list)

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft trips can be deleted.'))
        return super().unlink()

    @api.constrains('cargo_weight_kg','vehicle_id')
    def _check_cargo_weight(self):
        for rec in self:
            if rec.cargo_weight_kg <= 0:
                raise ValidationError(_('Cargo weight must be greater than zero.'))
            if rec.vehicle_id and rec.cargo_weight_kg > rec.vehicle_id.max_load_kg:
                raise ValidationError(_("Cargo weight (%s kg) exceeds the maximum load capacity of %s (%s kg).") % (
                    rec.cargo_weight_kg, rec.vehicle_id.display_name or rec.vehicle_id.name, rec.vehicle_id.max_load_kg))

    @api.depends('end_odometer_km','start_odometer_km','state')
    def _compute_actual_distance(self):
        for rec in self:
            if rec.state == 'completed' and rec.end_odometer_km and rec.start_odometer_km is not None:
                try:
                    rec.actual_distance_km = max(rec.end_odometer_km - rec.start_odometer_km, 0.0)
                except Exception:
                    rec.actual_distance_km = 0.0
            else:
                rec.actual_distance_km = 0.0

    def action_dispatch(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft trips can be dispatched.'))
            vehicle = rec.vehicle_id
            driver = rec.driver_id
            # Vehicle availability
            if vehicle.status != 'available':
                raise UserError(_('Vehicle %s is not available for dispatch (current status: %s).')
                                % (vehicle.display_name or vehicle.name, vehicle.status))
            # Driver availability
            if driver.status != 'available':
                raise UserError(_('Driver %s is not available for dispatch (current status: %s).')
                                % (driver.display_name or driver.name, driver.status))
            # License expiry
            if driver.license_expiry and driver.license_expiry < fields.Date.context_today(self):
                raise UserError(_("Driver %s's license expired on %s. Assignment blocked.")
                                % (driver.display_name or driver.name, driver.license_expiry))

            # Perform state changes atomically (ORM will wrap transaction)
            rec.start_odometer_km = vehicle.odometer_km or 0.0
            rec.dispatch_datetime = fields.Datetime.now()
            rec.state = 'dispatched'
            vehicle.status = 'on_trip'
            driver.status = 'on_trip'
        return True

    def action_complete(self):
        fuel_model = self.env.get('transitops.fuel.log')
        for rec in self:
            if rec.state != 'dispatched':
                raise UserError(_('Only dispatched trips can be completed.'))
            if not rec.end_odometer_km:
                raise UserError(_('Enter the end odometer reading before completing the trip.'))
            if rec.end_odometer_km < (rec.start_odometer_km or 0.0):
                raise UserError(_('End odometer (%s km) cannot be less than start odometer (%s km).')
                                % (rec.end_odometer_km, rec.start_odometer_km))

            # Update vehicle odometer and statuses
            vehicle = rec.vehicle_id
            driver = rec.driver_id
            vehicle.odometer_km = rec.end_odometer_km
            rec.complete_datetime = fields.Datetime.now()
            rec.state = 'completed'
            # compute actual_distance handled by compute
            # restore statuses
            try:
                driver.status = 'available'
            except Exception:
                _logger.exception('Failed to set driver status to available for %s', rec.id)
            try:
                vehicle.status = 'available'
            except Exception:
                _logger.exception('Failed to set vehicle status to available for %s', rec.id)

            # Create fuel log if provided
            if rec.fuel_consumed_l and rec.fuel_consumed_l > 0 and fuel_model:
                try:
                    fuel_model.create({
                        'vehicle_id': vehicle.id,
                        'trip_id': rec.id,
                        'date': fields.Date.context_today(self),
                        'liters': rec.fuel_consumed_l,
                        'cost': rec.fuel_cost or 0.0,
                        'odometer_km': rec.end_odometer_km,
                        'source': 'trip',
                    })
                except Exception:
                    _logger.exception('Failed to create fuel log from trip %s', rec.id)
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state not in ('draft','dispatched'):
                raise UserError(_('Completed trips cannot be cancelled.'))
            was_dispatched = (rec.state == 'dispatched')
            rec.state = 'cancelled'
            if was_dispatched:
                # restore resources
                try:
                    rec.vehicle_id.status = 'available'
                except Exception:
                    _logger.exception('Failed to restore vehicle status for cancelled trip %s', rec.id)
                try:
                    rec.driver_id.status = 'available'
                except Exception:
                    _logger.exception('Failed to restore driver status for cancelled trip %s', rec.id)
        return True
