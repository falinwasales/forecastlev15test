# -*- coding: utf-8 -*-
from odoo import fields, models, api


class Vessel(models.Model):
    _name = 'fce.vessel'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Vessel"

    name = fields.Char(string="Vessel ID")
    vessel_full_name = fields.Char(string="Vessel Name")
    vessel_operator = fields.Many2one('res.partner', string='Feeder Operator')
    nationality = fields.Many2one('res.country', string='Nationality')
    imo_number = fields.Char('IMO Number')
    loa = fields.Char('LOA')
    grt = fields.Integer('GRT')
    year_built = fields.Integer('Year Built')
    active = fields.Boolean(default=False)

    _sql_constraints = [('unique_name', 'unique (name)', 'Vessel ID must be unique!!')]

    def action_approve(self):
        for vessel in self:
            vessel.active = True

    def name_get(self):
        res = []
        for vessel in self:
            res.append((vessel.id, "%s" % (vessel.name)))
        return res
