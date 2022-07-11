# -*- coding: utf-8 -*-
from odoo import fields, models, api
import datetime
import logging
_logger = logging.getLogger(__name__)


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    container_owner = fields.Selection([
        ('soc', 'SOC'),
        ('coc', 'COC'),
    ])
    fal_move_ids_without_package = fields.Many2many('stock.move.line', compute='_fal_get_move_line')
    principal_id = fields.Many2one(
        'res.partner', domain="[('is_principal', '=', True)]",
        string="Principal")
    tare = fields.Float(string="Tare")
    idle_days = fields.Char(string="Idle Days", compute='_calculate_idle_days')

    def _fal_get_move_line(self):
        for lot in self:
            mv_lines = []
            for quant in lot.quant_ids:
                move_lines = quant.action_view_stock_moves()
                domain = move_lines['domain']
                mv_lines += self.env['stock.move.line'].search(domain).ids
            lot.fal_move_ids_without_package = [(6, 0, mv_lines)]

    def _calculate_idle_days(self):
        for lot in self:
            move_line_date = self.env['stock.move.line']
            date_now = fields.Datetime.now()
            for move_line in self.fal_move_ids_without_package.sorted('date', reverse=True):
                move_line_date = move_line
                break
            if move_line_date.location_id.quant_ids.filtered(lambda a: a.lot_id.id == lot.id):
                if move_line_date.actual_gate:
                    lot.idle_days = abs(move_line_date.actual_gate - date_now)
                else:
                    lot.idle_days = abs(move_line_date.date - date_now)
            else:
                lot.idle_days = '0 Days'

# class StockMoveLine(models.Model):
#     _inherit = "stock.move.line"

#     @api.model_create_multi
#     def create(self, vals_list):
#         mls = super(StockMoveLine, self).create(vals_list)
#         for ml in mls:
#             ml.write({'lot_id': False})
#         return mls
