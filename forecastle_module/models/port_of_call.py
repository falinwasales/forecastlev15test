# -*- coding: utf-8 -*-
from odoo import fields, models
from datetime import datetime


class PortOfCall(models.Model):
    _name = 'fce.port.of.call'
    _description = "Port Of Call"

    name = fields.Char(string="Name")
    port_type = fields.Selection([
        ('pol', 'POL'),
        ('pot', 'POT'),
        ('pod', 'POD')], required=True)
    port_code_id = fields.Many2one('fce.port.code', string='Port Code', required=True)
    voyage_id = fields.Many2one('fce.voyage', string='Voyage id')
    opening_date = fields.Datetime("Open Stack")
    closing_date = fields.Datetime("Closing Date")
    date_etd = fields.Date("ETD", help="Estimated Time Departure")
    date_eta = fields.Date("ETA", help="Estimated Time Arrival")
    date_td = fields.Date("ATD", help="Actual Time Departure")
    date_ta = fields.Date("ATA", help="Actual Time Arrival")
    closing_document = fields.Datetime(string="Closing Document")

    def name_get(self):
        res = []
        for poc in self:
            res.append((poc.id, "%s" % (poc.port_code_id.name)))
        return res
