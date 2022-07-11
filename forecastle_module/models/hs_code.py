# -*- coding: utf-8 -*-
from odoo import fields, models, api


class HSCode(models.Model):
    _name = 'fce.hs.code'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "HS Code"

    name = fields.Char(string="HS Code")
    commodity = fields.Char("Commodity", required="True")
    digit_categories = fields.Char(string="4 Digit Categories", required="True")
    product_description = fields.Char(string="Product Description")
    active = fields.Boolean(default=False)
    _sql_constraints = [('hs_code_unique', 'unique (name)', 'HS CODE must be unique!!')]

    def action_approve(self):
        for hs_code in self:
            hs_code.active = True

    def name_get(self):
        res = []
        for hs in self:
            res.append((hs.id, "%s - %s" % (hs.digit_categories, hs.commodity)))
        return res
