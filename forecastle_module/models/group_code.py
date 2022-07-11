# -*- coding: utf-8 -*-
from odoo import fields, models, api


class GroupName(models.Model):
    _name = 'fce.group.code'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Group Code"

    code = fields.Char(string=" Group Code")
    name = fields.Char(string="Group Name")
    active = fields.Boolean(default=False)
    _sql_constraints = [('unique_code', 'unique (code)', 'Group Code must be unique!!')]

    def action_approve(self):
        for group_code in self:
            group_code.active = True

    def name_get(self):
        res = []
        for gco in self:
            res.append((gco.id, "%s" % (gco.name)))
        return res
