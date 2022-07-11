from odoo import api, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    fal_consolidation_account_id = fields.Many2one('account.account', string="Consolidation Account", related='account_id.fal_consolidation_account_id', store=True)
