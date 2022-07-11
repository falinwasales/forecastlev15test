# -*- coding: utf-8 -*-
from odoo import fields, models


class IrReports(models.Model):
    _inherit = 'ir.actions.report'

    principal_id = fields.Many2one('res.partner', domain="[('is_principal', '=', True)]")
    forecastle_report_type = fields.Selection([
        ('other', 'Regular'),
        ('si', 'Shipping Instruction'),
        ('bl', 'Bill of Lading'),
    ], required=False, default='other')
