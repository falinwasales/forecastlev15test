from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class HrExpense(models.Model):
    _inherit = "hr.expense"

    fal_res_partner = fields.Many2one('res.partner', string="Vendor Expense")
