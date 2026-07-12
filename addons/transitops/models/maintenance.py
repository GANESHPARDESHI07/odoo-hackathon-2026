from odoo import fields, models, _
from odoo.exceptions import UserError


class TransitopsMaintenance(models.Model):
    _name = 'transitops.maintenance'
    _description = 'Maintenance'
    _inherit = ['mail.thread']
    _order = 'date desc, id desc'

    service_type = fields.Selection(
        [('oil_change', 'Oil Change'), ('tyres', 'Tyres'), ('brakes', 'Brakes'), ('engine', 'Engine'), ('electrical', 'Electrical'), ('general', 'General Service'), ('other', 'Other')],
        required=True,
        default='general',
    )
    vehicle_id = fields.Many2one('transitops.vehicle', required=True, tracking=True)
    date = fields.Date(required=True, default=lambda self: fields.Date.context_today(self))
    cost = fields.Float(default=0.0, tracking=True)
    state = fields.Selection(
        [('open', 'Open'), ('done', 'Done'), ('cancelled', 'Cancelled')],
        default='open',
        required=True,
        tracking=True,
    )
    description = fields.Text()

    def create(self, vals_list):
        # BR-09 / BR-16
        records = super().create(vals_list)
        for vals, record in zip(vals_list, records):
            if vals.get('state', 'open') == 'open' and record.vehicle_id:
                if record.vehicle_id.status != 'available':
                    raise UserError(
                        _('Maintenance can only be opened for vehicles that are Available (current status: {status}).').format(
                            status=record.vehicle_id.status
                        )
                    )
                record.vehicle_id.status = 'in_shop'
        return records

    def action_close(self):
        # BR-10
        for record in self:
            if record.state != 'open':
                raise UserError(_('Only open maintenance can be closed.'))
            record.state = 'done'
            record._release_vehicle()
        return True

    def action_cancel(self):
        # BR-10
        for record in self:
            if record.state != 'open':
                raise UserError(_('Only open maintenance can be cancelled.'))
            record.state = 'cancelled'
            record._release_vehicle()
        return True

    def _release_vehicle(self):
        # BR-10
        for record in self:
            if not record.vehicle_id:
                continue
            other_open = self.env['transitops.maintenance'].search([
                ('vehicle_id', '=', record.vehicle_id.id),
                ('state', '=', 'open'),
                ('id', '!=', record.id),
            ])
            if record.vehicle_id.status == 'in_shop' and not other_open:
                record.vehicle_id.status = 'available'
