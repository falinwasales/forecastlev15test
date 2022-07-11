# Copyright 2019 VentorTech OU
# License OPL-1.0 or later.

from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    autoprint_paperformat_id = fields.Many2one(
        comodel_name='printnode.paper',
        string='Autoprint Paper Format',
        help=(
            'This settings defines which paperformat '
            'should be chosen for printing lables of this carrier.'
        ),
    )
