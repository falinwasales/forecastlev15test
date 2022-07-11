# -*- coding: utf-8 -*-
from odoo import fields, models


class SlotOwner(models.Model):
    _name = 'fce.slot.owner'
    _description = "Feeder Slot"
    _rec_name = "vendor_ids"

    vendor_ids = fields.Many2one('res.partner', string='Vendor')
    voyage_id = fields.Many2one('fce.voyage', string='Voyage')
    capacity = fields.Integer(string='Capacity')
