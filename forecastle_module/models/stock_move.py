from odoo import models, fields, api, _
import logging
import datetime
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    principal_id = fields.Many2one('res.partner', string='Principal', domain=[('is_principal', '=', True)])

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for picking in self:
            detentions = []
            sale_import = False
            for move in picking.move_ids_without_package:
                detentions += move.purchase_line_id.import_container_info_id
                sale_import = move.purchase_line_id.import_container_info_id.sale_id

            if detentions:
                vals = {
                    'partner_id': sale_import.imp_principal_id.id,
                    'sales_source_id': sale_import.id,
                    'so_detention_id': sale_import.id,
                    'order_line': [],
                }
                invoice_lines = []
                for detention in detentions:
                    idr = self.env.ref('base.IDR')
                    vals.update({'currency_id': detention.currency_id.id})
                    product = self.env['product.product'].search([('is_detention', '=', True)], limit=1)
                    if not product:
                        raise UserError(_('Please set detention product'))

                    if not detention.actual_gate:
                        raise UserError(_('Please set actual gate in depo'))

                    actual_detention_charge = detention.actual_detention_charge
                    if detention.currency_id != idr:
                        actual_detention_charge = detention.currency_id._convert(
                            detention.actual_detention_charge,
                            idr,
                            picking.company_id,
                            picking.scheduled_date or fields.Date.today()
                        )

                    vals['order_line'].append((0, 0, {
                        'product_id': product.id,
                        'account_analytic_id': sale_import.analytic_account_id.id,
                        'name': detention.product_id.display_name,
                        'import_container_info_id': detention.id,
                        'price_unit': detention.actual_detention_charge,
                    }))

                    # Converted to idr
                    invoice_lines.append((0, 0, {
                        'product_id': product.id,
                        'name': detention.product_id.display_name,
                        'price_unit': actual_detention_charge,
                        'analytic_account_id': sale_import.analytic_account_id.id,
                    }))
                purchase = self.env['purchase.order'].create(vals)
                invoice_vals = purchase._fal_prepare_invoice()
                invoice_vals['partner_id'] = sale_import.partner_id.id
                invoice_vals['currency_id'] = self.env.ref('base.IDR').id
                invoice_vals['invoice_line_ids'] = invoice_lines
                move = self.env['account.move'].create(invoice_vals)
                sale_import.detention_invoice_id = move.id
                sale_import.detention_invoice_id.fal_invoice_type = 'invoice'
                sale_import.write({'po_detention_id': purchase.id})
        return res

    def action_fix_unreserved_quants(self):
        quants = self.env["stock.quant"].search([])

        move_line_ids = []

        warning = ""

        for quant in quants:

            move_lines = self.env["stock.move.line"].search(

                [

                    ("product_id", "=", quant.product_id.id),

                    ("location_id", "=", quant.location_id.id),

                    ("lot_id", "=", quant.lot_id.id),

                    ("package_id", "=", quant.package_id.id),

                    ("owner_id", "=", quant.owner_id.id),

                    ("product_qty", "!=", 0),

                ]

            )

            move_line_ids += move_lines.ids

            reserved_on_move_lines = sum(move_lines.mapped("product_qty"))

            move_line_str = str.join(

                ", ", [str(move_line_id) for move_line_id in move_lines.ids]

            )


            if quant.location_id.should_bypass_reservation():

                # If a quant is in a location that should bypass the reservation, its `reserved_quantity` field

                # should be 0.

                if quant.reserved_quantity != 0:

                    quant.write({"reserved_quantity": 0})

            else:

                # If a quant is in a reservable location, its `reserved_quantity` should be exactly the sum

                # of the `product_qty` of all the partially_available / assigned move lines with the same

                # characteristics.

                if quant.reserved_quantity == 0:

                    if move_lines:

                        move_lines.with_context(bypass_reservation_update=True).write(

                            {"product_uom_qty": 0}

                        )

                elif quant.reserved_quantity < 0:

                    quant.write({"reserved_quantity": 0})

                    if move_lines:

                        move_lines.with_context(bypass_reservation_update=True).write(

                            {"product_uom_qty": 0}

                        )

                else:

                    if reserved_on_move_lines != quant.reserved_quantity:

                        move_lines.with_context(bypass_reservation_update=True).write(

                            {"product_uom_qty": 0}

                        )

                        quant.write({"reserved_quantity": 0})

                    else:

                        if any(move_line.product_qty < 0 for move_line in move_lines):

                            move_lines.with_context(bypass_reservation_update=True).write(

                                {"product_uom_qty": 0}

                            )

                            quant.write({"reserved_quantity": 0})


        move_lines = self.env["stock.move.line"].search(

            [

                ("product_id.type", "=", "product"),

                ("product_qty", "!=", 0),

                ("id", "not in", move_line_ids),

            ]

        )


        move_lines_to_unreserve = []


        for move_line in move_lines:

            if not move_line.location_id.should_bypass_reservation():

                move_lines_to_unreserve.append(move_line.id)


        if len(move_lines_to_unreserve) > 1:

            self.env.cr.execute(

                """

                    UPDATE stock_move_line SET product_uom_qty = 0, product_qty = 0 WHERE id in %s ;

                """

                % (tuple(move_lines_to_unreserve),)

            )

        elif len(move_lines_to_unreserve) == 1:

            self.env.cr.execute(

                """

                UPDATE stock_move_line SET product_uom_qty = 0, product_qty = 0 WHERE id = %s ;

                """

                % (move_lines_to_unreserve[0])

            )


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        res = super(StockMove, self)._get_new_picking_values()
        operation_type = self.env['stock.picking.type'].search([('fal_user_depo_id', '=', self.sale_line_id.order_id.depot_name_id.depot_id.id)])
        res['principal_id'] = self.mapped('sale_line_id.order_id.principal_id').id
        if self.sale_line_id.order_id.is_import:
            res['picking_type_id'] = operation_type.filtered(lambda a: a.code == 'incoming').id
        else:
            res['picking_type_id'] = operation_type.filtered(lambda a: a.code == 'outgoing').id
        return res


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial Number',
        domain="[('product_id', '=', product_id), ('id', 'in', available_lot_ids)]")
    available_lot_ids = fields.Many2many('stock.production.lot', compute='_get_available_lots')
    consignee_id = fields.Many2one('res.partner', string="Consignee")
    principal_id = fields.Many2one('res.partner', string="Principal", domain="[('is_principal', '=', True)]")
    actual_gate = fields.Datetime(string="Actual Gate in Depo", store=True)
    actual_gate_out = fields.Datetime(string="Actual Gate Out")
    repaired_by = fields.Selection([('consignee', 'Consignee'), ('principal', 'Principal')], string="Repaired By")
    photo = fields.Binary(string="File")
    filename = fields.Char(string="Filename")
    repair_value = fields.Float(string="Repair Value", compute='_get_repair_value')
    remark = fields.Text(string="Remarks")
    fce_repair_id = fields.Many2one('fce.repair', string="Repair")
    condition = fields.Selection([('av', 'AV'), ('dm', 'DM')], string="Condition")
    repair_status = fields.Selection([('waiting_approval', 'Waiting approval'), ('on_Process', 'On Process'), ('complete_repair', 'Complete Repair')], string="Repair Status")
    start_repair_date = fields.Date(string="Start Repair Date")
    complete_repair_date = fields.Date(string="Complete Repair Date")
    grade = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C')], string="Grade")
    tare = fields.Float(string="Tare")
    max_gross_weight = fields.Integer(string="Max Gross Weight")
    container_state = fields.Selection([
        ('none', 'None'),
        ('gate_in', 'GATE IN'),
        ('gate_out', 'GATE OUT')], string='Status', readonly=True, default='none', compute='_container_state')
    loading_date = fields.Date(string="Loading Date")
    gate_in_cy = fields.Date(string="Gate In CY")
    discharge_date = fields.Date(string="Discharge Date")
    gate_out_cy = fields.Date(string="Gate Out CY")
    idle_days = fields.Char(string='Idle Days', compute='_calculate_date')
    idle = fields.Char(string='Idle Days')
    pelabuhan_asal = fields.Many2one('fce.port.code', 'Pelabuhan Asal')
    pod_id = fields.Many2one('fce.port.code', 'POD')

    def _get_repair_value(self):
        for line in self:
            sale = line.move_id.purchase_line_id.order_id.sales_source_id
            purchase_line_id = False
            for po in sale.po_repair_consignee_ids:
                for order_line in po.order_line.filtered(lambda a: line.lot_id == a.container_no_id):
                    purchase_line_id = order_line
            if not purchase_line_id:
                for po in sale.po_repair_ids:
                    for order_line in po.order_line.filtered(lambda a: line.lot_id == a.container_no_id):
                        purchase_line_id = order_line
            line.repair_value = purchase_line_id and purchase_line_id.price_subtotal or 0

    @api.onchange('actual_gate')
    def _change_actual_gate(self):
        self.move_id.purchase_line_id.import_container_info_id.actual_gate = self.actual_gate

    @api.depends('location_id', 'product_id', 'picking_id', 'picking_id.location_id')
    def _get_available_lots(self):
        for line in self:
            quants = line.location_id.quant_ids.filtered(lambda a: a.product_id == line.product_id)
            lots = quants.mapped('lot_id')

            if line.picking_code == 'incoming':
                lots = self.env['stock.production.lot'].search([('product_id', '=', line.product_id.id)])

            line.available_lot_ids = [(6, 0, lots.ids)]

    @api.depends('product_id')
    def _container_state(self):
        for x in self:
            if x.picking_id.picking_type_id.code == 'incoming':
                x.container_state = 'gate_in'
            elif x.picking_id.picking_type_id.code == 'outgoing':
                x.container_state = 'gate_out'
            else:
                x.container_state = False
            if x.picking_id.picking_type_id.code == 'outgoing':
                x.container_state = 'gate_out'

    def _calculate_date(self):
        for x in self:
            if x.picking_id.picking_type_id.code == 'incoming' and x.actual_gate:
                date_now = fields.Datetime.now()
                quant = x.picking_id.location_dest_id.quant_ids.filtered(lambda a: a.lot_id == x.lot_id)
                if quant:
                    x.idle_days = x.actual_gate - date_now
                else:
                    if x.idle is False and x.picking_id.state == 'done':
                        x.idle = x.actual_gate - date_now
                    else:
                        x.idle_days = False
            else:
                x.idle_days = False

    @api.onchange('lot_id', 'tare')
    def _onchange_partner_id(self):
        # import(receipt)
        if self.picking_code == 'incoming':
            self.lot_id.tare = self.tare
        # eksport(delivery)
        if self.picking_code == 'outgoing':
            self.tare = self.lot_id.tare


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    principal_id = fields.Many2one('res.partner', related='lot_id.principal_id', store=True)
