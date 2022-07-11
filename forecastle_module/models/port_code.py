# -*- coding: utf-8 -*-
from odoo import fields, models, api


class PortCode(models.Model):
    _name = 'fce.port.code'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Port Code"

    name = fields.Char(string="Port ID")
    port_full_name = fields.Char(string="Name")
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    coutry_id = fields.Many2one('res.country', string='Country')
    terminal_code_ids = fields.One2many('fce.terminal.code', 'port_code_id', string='Terminal Code')
    
    active = fields.Boolean(default=False)
    _sql_constraints = [('port_id_unique', 'unique (name)', 'Port ID must be unique!!')]

    def action_approve(self):
        for port_code in self:
            port_code.active = True

    def name_get(self):
        res = []
        for pco in self:
            res.append((pco.id, "%s" % (pco.name)))
        return res

    @api.onchange('coutry_id')
    def _onchange_country_id(self):
        if self.coutry_id and self.coutry_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id.country_id:
            self.coutry_id = self.state_id.country_id


class AgentCode(models.Model):
    _name = 'fce.agent.code'

    principal_id = fields.Many2one('res.partner', string="Principal")
    port_code_id = fields.Many2one('fce.port.code')
    agent_id = fields.Many2one('res.partner', string="Agent", domain="[('is_agent', '=', True)]")
    agent_code = fields.Char()

    def name_get(self):
        res = []
        for agent in self:
            res.append((agent.id, "%s" % (agent.agent_code)))
        return res
