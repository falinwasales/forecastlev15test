from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ResCurrencies(models.Model):
    _inherit = "res.currency.rate"

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

class Currency(models.Model):
    _inherit = "res.currency"

    name = fields.Char(string='Currency', required=True, help="Currency Code (ISO 4217)")
    description = fields.Char(string='Description')

    def name_get(self):
        res = []
        for currency in self:
            if currency.description:
                res.append((currency.id, "%s - %s" % (currency.name, currency.description)))
            else:
                res.append((currency.id, "%s" % (currency.name)))
        return res
