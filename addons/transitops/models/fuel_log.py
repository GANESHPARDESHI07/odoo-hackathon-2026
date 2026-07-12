from odoo import api, fields, models, _


class TransitopsFuelLog(models.Model):
    _name = 'transitops.fuel.log'
    _description = 'Fuel Log'

    vehicle_id = fields.Many2one('transitops.vehicle', required=True, ondelete='cascade')
    trip_id = fields.Many2one('transitops.trip', ondelete='set null')
    date = fields.Date(required=True)
    liters = fields.Float(required=True)
    cost = fields.Float(required=True, default=0.0)
    odometer_km = fields.Float()
    source = fields.Selection([('manual','Manual'),('trip','From Trip')], default='manual')
