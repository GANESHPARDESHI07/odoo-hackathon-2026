from odoo import api, fields, models, _


class TransitopsDriver(models.Model):
    _name = 'transitops.driver'
    _description = 'Driver'

    name = fields.Char(required=True)
    license_no = fields.Char(required=True, index=True, copy=False)
    license_category = fields.Selection([('lmv','LMV'),('hmv','HMV'),('both','LMV + HMV')], default='lmv')
    license_expiry = fields.Date(required=True)
    safety_score = fields.Float(default=80.0)
    status = fields.Selection([('available','Available'),('on_trip','On Trip'),('off_duty','Off Duty'),('suspended','Suspended')], default='available', required=True, index=True)
