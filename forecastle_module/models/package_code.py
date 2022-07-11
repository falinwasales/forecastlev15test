# -*- coding: utf-8 -*-
from odoo import fields, models, api


class GroupName(models.Model):
    _name = 'fce.package.code'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Package Code"

    code = fields.Char(string=" Package Code")
    name = fields.Char(string=" Package Name")
    package_code = fields.Char(string=" Package", compute="_code")
    active = fields.Boolean(default=False)
    _sql_constraints = [('unique_package_code', 'unique (code)', 'Package Code must be unique!!')]

    def action_approve(self):
        for package in self:
            package.active = True

    def name_get(self):
        res = []
        for p in self:
            res.append((p.id, "%s" % (p.name)))
        return res
