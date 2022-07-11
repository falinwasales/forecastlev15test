from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class StockLocation(models.Model):
    _inherit = 'stock.location'

    principal_ids = fields.Many2many('res.partner', string="Principal", domain=[('is_principal', '=', True)])
    depot_id = fields.Many2one('res.partner', string="Depot", domain="[('is_depot', '=', True)]")
