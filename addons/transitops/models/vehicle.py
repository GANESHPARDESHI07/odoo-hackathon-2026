from odoo import api, fields, models, _


class TransitopsVehicle(models.Model):
    _name = 'transitops.vehicle'
    _description = 'Vehicle'

    name = fields.Char(required=True)
    registration_no = fields.Char(required=True, index=True, copy=False)
    vehicle_type = fields.Selection([('truck','Truck'),('van','Van'),('bus','Bus'),('car','Car'),('bike','Bike')], default='van')
    region = fields.Selection([('north','North'),('south','South'),('east','East'),('west','West'),('central','Central')], default='west')
    max_load_kg = fields.Float(required=True, default=0.0)
    odometer_km = fields.Float(default=0.0)
    acquisition_cost = fields.Float(default=0.0)
    status = fields.Selection([('available','Available'),('on_trip','On Trip'),('in_shop','In Shop'),('retired','Retired')], default='available', required=True, index=True)
