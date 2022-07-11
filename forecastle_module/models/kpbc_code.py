# -*- coding: utf-8 -*-
from odoo import fields, models


class GroupName(models.Model):
    _name = 'fce.kpbc.code'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "KPBC Code"

    kpbc_code = fields.Char(string=" KPBC Code")
    name = fields.Char(string="KPBC Name")
    active = fields.Boolean(default=False)
    _sql_constraints = [('unique_kpbc_code', 'unique (kpbc_code)', 'KPBC Code must be unique!!')]

    def action_approve(self):
        for kpbc in self:
            kpbc.active = True

    def name_get(self):
        res = []
        for kcbp in self:
            res.append((kcbp.id, "%s - %s" % (kcbp.kpbc_code, kcbp.name)))
        return res
