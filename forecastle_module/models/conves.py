# -*- coding: utf-8 -*-
from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)


class ConnectingVessel(models.Model):
    _name = 'fce.conves'
    _description = "Connecting Vessel"

    port_code_id = fields.Many2one('fce.port.code', string='Port Code')
    port_type = fields.Selection([
        ('pol', 'POL'),
        ('pot', 'POT'),
        ('pod', 'POD')])
    agent_id = fields.Many2one('res.partner', string="Agent", compute="_get_agent_code")
    agent_code_id = fields.Many2one('fce.agent.code', string="Agent Code", compute="_get_agent_code")
    vessel_id = fields.Many2one('fce.vessel', string='Vessel')
    voyage_id = fields.Many2one('fce.voyage', string='Voyage')
    sale_id = fields.Many2one('sale.order', string='Sale')
    date_etd = fields.Date(string="ETD")
    date_eta = fields.Date(string="ETA")
    time_departure = fields.Date(string="Time Departure")
    time_arrival = fields.Date(string="Time Arrival")

    @api.onchange('voyage_id')
    def _onchange_voyage_id(self):
        poc = self.env['fce.port.of.call']
        pot = self.voyage_id.port_of_call_ids.filtered(lambda x: x.port_type == 'pot')
        pod = self.voyage_id.port_of_call_ids.filtered(lambda x: x.port_type == 'pod')
        pol = self.voyage_id.port_of_call_ids.filtered(lambda x: x.port_type == 'pol')
        if pot:
            poc = pot[-1]
        elif pod:
            poc = pod[-1]
        elif pol:
            poc = pol[-1]

        self.port_code_id = poc.port_code_id.id
        self.port_type = poc.port_type
        self.vessel_id = self.voyage_id.vessel_id.id
        self.date_etd = poc.date_etd
        self.date_eta = poc.date_eta
        self.time_departure = poc.date_td
        self.time_arrival = poc.date_ta

    def name_get(self):
        res = []
        for conves in self:
            res.append((conves.id, "%s" % (conves.id)))
        return res

    @api.depends('sale_id', 'sale_id.principal_id', 'port_code_id')
    def _get_agent_code(self):
        for conves in self:
            agent_codes = conves.sale_id.principal_id.fal_agent_code_ids.filtered(lambda a: a.port_code_id == conves.port_code_id)
            agent_id = False
            agent_code_id = False
            for agent in agent_codes:
                if not agent_code_id:
                    agent_id = agent.agent_id.id
                    agent_code_id = agent.id
            conves.agent_id = agent_id
            conves.agent_code_id = agent_code_id
