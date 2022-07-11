# -*- coding: utf-8 -*-
from odoo import fields, models, api
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class fce_voyage(models.Model):
    _name = 'fce.voyage'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Schedule"

    def name_get(self):
        res = []
        for voyage in self:
            res.append((voyage.id, "%s" % (voyage.name)))
        return res

    name = fields.Char(string="Voyage")
    vessel_id = fields.Many2one('fce.vessel', string='Vessel')
    date_etd = fields.Date(string="ETD", help="Estimated Time Arrival", compute='_compute_etd')
    date_eta = fields.Date(string="ETA", help="Estimated Time Arrival", compute='_compute_eta')
    date_td = fields.Date(string="ATD", help="Actual Time Departure", compute='_compute_date_td')
    date_ta = fields.Date(string="ATA", help="Actual Time Arrival", compute='_compute_date_ta')
    terminal_id = fields.Many2one('fce.terminal.code', string='Terminal Code')
    carrier_id = fields.Many2one('res.partner', string='Feeder Operator')
    slot_owner_ids = fields.One2many('fce.slot.owner', 'voyage_id', string='Slot Owner')
    port_of_call_ids = fields.One2many('fce.port.of.call', 'voyage_id', string='Port Of Call', copy=True)
    re_port_code_id = fields.Many2one(related='terminal_id.port_code_id')
    pol_id = fields.Many2one('fce.port.of.call', 'PoL', compute="_get_pol")
    pod_id = fields.Many2one('fce.port.of.call', 'PoD', compute="_get_pod")
    # closing_document = fields.Date(string="Closing Document")
    need_connecting_vessel = fields.Boolean(string="Need Connecting Vessel")
    active = fields.Boolean(default=False)

    ##############################################
    # Compute Logic
    @api.constrains('slot_owner_ids')
    def _check_owner_ids(self):
        for record in self:
            if not record.slot_owner_ids:
                raise ValidationError("Please fill the feeder slot")

    @api.depends('port_of_call_ids', 'port_of_call_ids.date_etd')
    def _compute_etd(self):
        for voyage in self:
            port_type = voyage.port_of_call_ids.filtered(lambda poc: poc.port_type == 'pol')
            voyage.date_etd = port_type and port_type[0].date_etd or False

    @api.depends('port_of_call_ids', 'port_of_call_ids.date_eta')
    def _compute_eta(self):
        for voyage in self:
            port_type = voyage.port_of_call_ids.filtered(lambda poc: poc.port_type == 'pod')
            voyage.date_eta = port_type and port_type[0].date_eta or False

    @api.depends('port_of_call_ids', 'port_of_call_ids.date_eta')
    def _get_pol(self):
        for voyage in self:
            port_type = voyage.port_of_call_ids.filtered(lambda poc: poc.port_type == 'pol')
            voyage.pol_id = port_type and port_type[0].id or False

    @api.depends('port_of_call_ids', 'port_of_call_ids.date_eta')
    def _get_pod(self):
        for voyage in self:
            port_type = voyage.port_of_call_ids.filtered(lambda poc: poc.port_type == 'pod')
            voyage.pod_id = port_type and port_type[0].id or False

    @api.depends('port_of_call_ids', 'port_of_call_ids.date_td')
    def _compute_date_td(self):
        for voyage in self:
            port_type = voyage.port_of_call_ids.filtered(lambda poc: poc.port_type == 'pol')
            voyage.date_td = port_type and port_type[0].date_td or False

    @api.depends('port_of_call_ids', 'port_of_call_ids.date_ta')
    def _compute_date_ta(self):
        for voyage in self:
            port_type = voyage.port_of_call_ids.filtered(lambda poc: poc.port_type == 'pod')
            voyage.date_ta = port_type and port_type[0].date_ta or False

    def action_approve(self):
        for voyage in self:
            voyage.active = True
