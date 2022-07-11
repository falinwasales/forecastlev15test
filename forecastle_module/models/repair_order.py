# -*- coding: utf-8 -*-
from odoo import fields, models, api


class FceRepair(models.Model):
    _name = 'fce.repair'

    name = fields.Char(string="Repair", readonly=True)
    total_repair_by_principal = fields.Float(string="Total Repair By Principal", compute="_compute_get_repair")
    total_repair_by_consignee = fields.Float(string="Total Repair By Consignee", compute="_compute_get_repair")
    total_repair = fields.Float(string="Total Repair By Consignee", compute="_compute_get_repair")
    receipt_ids = fields.One2many('stock.move.line', 'fce_repair_id', string="Receipt Orders", readonly=True)

    @api.model
    def create(self, vals):
        if not vals.get('name', False):
            seq_obj = self.env['ir.sequence']
            vals['name'] = seq_obj.next_by_code(
                'seq.repair') or '/'
        return super(FceRepair, self).create(vals)

    @api.depends('receipt_ids', 'receipt_ids.fce_repair_id')
    def _compute_get_repair(self):
        for repair in self:
            repair.total_repair_by_principal = sum(move.repair_value for move in repair.receipt_ids.filtered(lambda move: move.repaired_by == 'principal'))
            repair.total_repair_by_consignee = sum(move.repair_value for move in repair.receipt_ids.filtered(lambda move: move.repaired_by == 'consignee'))
            repair.total_repair = sum(move.repair_value for move in repair.receipt_ids)
