# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _


class AccountAccount(models.Model):
    _inherit = 'account.account'

    fal_is_consolidation = fields.Boolean('Is Consolidation', help="Tag this account as consolidation account")
    fal_consolidation_account_id = fields.Many2one('account.account', string="Consolidation Account", domain="[('fal_is_consolidation', '=', True)]", store=True)
