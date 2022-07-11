# -*- coding: utf-8 -*-
from odoo import fields, models, api


class TerminalCode(models.Model):
    _name = 'fce.terminal.code'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Terminal Code"

    name = fields.Char(string="Terminal Code")
    terminal_full_name = fields.Char(string="Terminal Name")
    port_code_id = fields.Many2one('fce.port.code', string='Port Code')
    address = fields.Char(string="Terminal Address")
    _sql_constraints = [('terminal_code_unique', 'unique (name)', 'Terminal Code must be unique!!')]

    def name_get(self):
        res = []
        for tc in self:
            res.append((tc.id, "%s" % (tc.name)))
        return res
