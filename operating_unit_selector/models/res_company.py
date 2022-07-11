from odoo import fields, models, api, tools, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    operating_unit_ids = fields.One2many('operating.unit', 'company_id', string="Operating Unit(s)")
