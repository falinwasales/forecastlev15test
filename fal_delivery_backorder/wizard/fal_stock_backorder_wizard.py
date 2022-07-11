# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, Warning
import logging

_logger = logging.getLogger(__name__)


class FalStockBackorderWizard(models.TransientModel):
    _name = 'fal.stock.backorder.wizard'
    _description = 'Backorder Wizard'

    fal_picking_type_id = fields.Many2one('stock.picking.type', string="New Picking Operation")
    fal_location_id = fields.Many2one('stock.location', string="Source Location")
    fal_location_dest_id = fields.Many2one('stock.location', string="Destination Location")
    pick_ids = fields.Many2many('stock.picking', 'fal_stock_picking_backorder_rel')
    fal_stock_backorder_line_wizard_ids = fields.One2many('fal.stock.backorder.line.wizard', 'fal_stock_backorder_wizard_id', string='Backorder Wizard Line ID')

    scheduled_date = fields.Datetime(
        'Scheduled Date', default=fields.Datetime.now)

    is_over_qty = fields.Boolean('Is Qty Over', default=False, compute='_compute_is_over_qty')
    overprocessed_product_name = fields.Text(compute='_compute_is_over_qty')

    @api.depends('fal_stock_backorder_line_wizard_ids.is_over_qty', 'fal_stock_backorder_line_wizard_ids.fal_backorder_qty', 'fal_stock_backorder_line_wizard_ids.product_uom_qty', 'is_over_qty')
    def _compute_is_over_qty(self):
        for wizard in self:
            filtered = wizard.fal_stock_backorder_line_wizard_ids.filtered(lambda x: x.is_over_qty)
            wizard.overprocessed_product_name = ''
            if filtered:
                wizard.is_over_qty = True
                for line in filtered:
                    wizard.overprocessed_product_name = ''.join([wizard.overprocessed_product_name, line.product_id.display_name, '\n'])
            else:
                wizard.is_over_qty = False
                wizard.overprocessed_product_name = False

    # This method follows stock picking _create_backorder
    # Odoo Process are validating first intial stock move.
    # Because by Validating stock moves Odoo creates a new stock move inside the same stock.picking
    # by making backorder, Odoo create new picking and move all non finished move to the new picking
    # Here we should imitate Odoo method of 'validating' without really validating it.
    # TO CHECK ON MIGRATION (Migration Check by David, Can't action assign if no moves)
    def _process(self):
        backorders = self.env['stock.picking']
        qty_not_zero = sum(self.mapped('fal_stock_backorder_line_wizard_ids.fal_backorder_qty'))
        if qty_not_zero:
            wizard_lines = self.mapped('fal_stock_backorder_line_wizard_ids')
            for picking in self.pick_ids:
                if self.fal_picking_type_id and self.fal_location_id and self.fal_location_dest_id:
                    backorder_picking = picking.copy({
                        'name': '/',
                        'move_lines': [],
                        'move_line_ids': [],
                        'backorder_id': picking.id,
                        'scheduled_date': self.scheduled_date,
                        'picking_type_id': self.fal_picking_type_id.id,
                        'location_dest_id': self.fal_location_dest_id.id,
                        'location_id': self.fal_location_id.id
                    })
                else:
                    backorder_picking = picking.copy({
                        'name': '/',
                        'move_lines': [],
                        'move_line_ids': [],
                        'backorder_id': picking.id,
                        'scheduled_date': self.scheduled_date
                    })
                picking.message_post(
                    body=_('The backorder <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a> has been created.') % (
                        backorder_picking.id, backorder_picking.name))
                # For every backorder wizard and if there is value on backorder and value > 0. Check if backorder qty is more than initial
                # if it's less then make a copy of it and put onto new picking
                # else just move it to new picking
                for wizard_line in wizard_lines.filtered(lambda x: x.move_line_id in picking.move_lines and x.fal_backorder_qty > 0):
                    if wizard_line.fal_backorder_qty < wizard_line.move_line_id.product_uom_qty:
                        if self.fal_picking_type_id and self.fal_location_id and self.fal_location_dest_id:
                            wizard_line.move_line_id.copy({
                                'product_uom_qty': wizard_line.fal_backorder_qty,
                                'picking_id': backorder_picking.id,
                                'date': self.scheduled_date,
                                'picking_type_id': self.fal_picking_type_id.id,
                                'location_dest_id': self.fal_location_dest_id.id,
                                'location_id': self.fal_location_id.id
                            })
                        else:
                            wizard_line.move_line_id.copy({
                                'product_uom_qty': wizard_line.fal_backorder_qty,
                                'picking_id': backorder_picking.id,
                                'date': self.scheduled_date
                            })

                        wizard_line.move_line_id.write({'product_uom_qty': wizard_line.move_line_id.product_uom_qty - wizard_line.fal_backorder_qty})
                    elif wizard_line.fal_backorder_qty == wizard_line.move_line_id.product_uom_qty:
                        wizard_line.move_line_id.write({'picking_id': backorder_picking.id})
                        wizard_line.move_line_id.mapped('package_level_id').write({'picking_id': backorder_picking.id})
                        wizard_line.move_line_id.mapped('move_line_ids').write({'picking_id': backorder_picking.id})
                    else:
                        raise UserError(_('The quantity you want to backorder is more than initial quantity.'))
                back_order_moves = backorder_picking.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
                if back_order_moves:
                    backorder_picking.action_assign()
                moves = picking.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
                if moves:
                    picking.action_assign()
                backorders |= backorder_picking

    def process(self):
        self._process()

    @api.onchange('fal_picking_type_id')
    def onchange_picking_type(self):
        if self.fal_picking_type_id:
            if self.pick_ids[0]:
                if self.pick_ids[0].partner_id:
                    partner_val= self.pick_ids[0].partner_id
                else:
                    partner_val=False
            if self.fal_picking_type_id.default_location_src_id:
                fal_location_id = self.fal_picking_type_id.default_location_src_id.id
            elif partner_val:
                fal_location_id = partner_val.property_stock_supplier.id
            else:
                customerloc, fal_location_id = self.env['stock.warehouse']._get_partner_locations()

            if self.fal_picking_type_id.default_location_dest_id:
                fal_location_dest_id = self.fal_picking_type_id.default_location_dest_id.id
            elif partner_val:
                fal_location_dest_id = partner_val.property_stock_customer.id
            else:
                fal_location_dest_id, supplierloc = self.env['stock.warehouse']._get_partner_locations()

            self.fal_location_id = fal_location_id
            self.fal_location_dest_id = fal_location_dest_id


class FalStockBackorderLineWizard(models.TransientModel):
    _name = 'fal.stock.backorder.line.wizard'
    _description = 'Delivery Backorder Line Wizard'

    fal_backorder_qty = fields.Float(
        'Quantity to Backorder',
        digits='Product Unit of Measure',
        required=True,
        default=0.0)

    fal_stock_backorder_wizard_id = fields.Many2one('fal.stock.backorder.wizard', string='Backorder Wizard ID')
    move_line_id = fields.Many2one('stock.move', string='Stock Move')
    product_id = fields.Many2one('product.product', string='Product', related='move_line_id.product_id')
    product_uom_qty = fields.Float(
        'Initial Demand',
        digits='Product Unit of Measure',
        related='move_line_id.product_uom_qty')

    is_over_qty = fields.Boolean('Is Qty Over', default=False, compute='_compute_is_over_qty')

    @api.depends('fal_backorder_qty', 'product_uom_qty', 'is_over_qty')
    def _compute_is_over_qty(self):
        for line in self:
            if line.product_uom_qty < line.fal_backorder_qty:
                line.is_over_qty = True
            else:
                line.is_over_qty = False
