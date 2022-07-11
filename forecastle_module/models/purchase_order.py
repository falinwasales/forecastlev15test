# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    is_container_cost = fields.Boolean(string="Container Cost")
    is_receipt = fields.Boolean(string="Receipt")
    sales_source_id = fields.Many2one("sale.order", "Sales Source", copy=False, readonly=True)
    sales_source_id_is_import = fields.Many2one("sale.order", related='sales_source_id', copy=False, readonly=True, strore=True)
    so_detention_id = fields.Many2one("sale.order", "SO Detention", copy=False)
    so_id = fields.Many2one("sale.order", "Sale Order", copy=False)
    so_repair_id = fields.Many2one("sale.order", "Sale Order Repair", copy=False)
    is_repair = fields.Boolean("PO Repair", copy=False)
    so_repair_consignee_id = fields.Many2one("sale.order", "Sale Order Repair Consignee", copy=False)
    repair_invoice_id = fields.Many2one("account.move", "Invoice Repair", copy=False)
    commission_invoice_id = fields.Many2one('account.move', string="Commission Invoice", copy=False)
    expense_invoice_id = fields.Many2one('account.move', string="Expense Invoice", copy=False)
    principal_id = fields.Many2one('res.partner', string="Principal", domain="[('is_principal', '=', True)]", states=READONLY_STATES,)
    # related
    is_import = fields.Boolean(string="Is Import", related='sales_source_id.is_import')
    fal_vendor_type = fields.Selection([
        ('vendor_bill_c2c', 'VB C2C Container'),
        ('vendor_bill_feeder', 'VB Feeder Slot'),
        ('vb_repair', 'VB Repair'),
    ], string="Vendor Type")

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        self._create_invoice_commission()
        self._create_invoice_commission_import()
        self._create_invoice_expense()
        self._create_repair_invoice()
        self._auto_create_bill()
        self._create_detention_commission()
        self._auto_set_container_number()
        return res

    def _auto_set_container_number(self):
        for purchase in self:   
            for line in purchase.order_line.filtered(lambda a: a.import_container_info_id):
                moves_lines = self.env['stock.move.line'].search([('move_id.purchase_line_id', '=', line.id)])
                location_id = line.import_container_info_id.sale_id.depot_name_id
                if location_id:
                    for pick in purchase.picking_ids:
                        pick.sudo().write({'location_dest_id': location_id.id})
                        pick.move_line_ids_without_package.sudo().write({'location_dest_id': location_id.id, 'discharge_date': line.import_container_info_id.sale_id.discharge_date, 'gate_out_cy': line.import_container_info_id.sale_id.gate_out_cy_date})

                for move_line in moves_lines:
                    move_line.write({'lot_id': line.import_container_info_id.no_container_id.id, 'qty_done': line.product_qty, 'pelabuhan_asal': line.import_container_info_id.sale_id.pelabuhan_asal.id})

    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        operation_type = self.env['stock.picking.type'].search([('fal_user_depo_id', '=', self.sales_source_id_is_import.depot_name_id.depot_id.id)])
        if self.sales_source_id_is_import.is_import:
            res['picking_type_id'] = operation_type.filtered(lambda a: a.code == 'incoming').id
            res['principal_id'] = self.sales_source_id_is_import.imp_principal_id.id
        else:
            res['picking_type_id'] = operation_type.filtered(lambda a: a.code == 'outgoing').id
            res['picking_type_id'] = self.sales_source_id_is_import.imp_principal_id.id
        return res

    # for import
    def _create_detention_commission(self):
        for purchase in self:
            if purchase.partner_id.is_principal and purchase.so_detention_id:
                commission_product = purchase.partner_id.product_commission_id
                if not commission_product:
                    raise UserError(_('Please Set Commission Product on Principal: %s')% (purchase.partner_id.name,))

                invoice_vals = purchase._fal_prepare_invoice()
                invoice_vals['partner_id'] = purchase.partner_id.id
                invoice_vals['fal_invoice_mode'] = 'commission'
                invoice_vals['currency_id'] = self.env.ref('base.USD').id

                commission = self.env['commission.export'].search([
                    ('principal_id', '=', purchase.partner_id.id),
                ], limit=1)

                data_category = []
                res = {}

                for line in purchase.order_line.filtered(lambda a: a.product_id.is_detention):
                    data_category.append([line.import_container_info_id.size, line])

                for key, val in data_category:
                    if key in res:
                        res[key] += [val]
                    else:
                        res[key] = [val]

                for product_category in res:
                    lines = res[product_category]
                    commission_line = commission.commission_line_ids.filtered(lambda a: a.commission_type == 'detention' and a.product_category_id.id == product_category.id)
                    total_amount = 0

                    for line in lines:
                        if line.product_id.id in commission_line.product_ids.ids:
                            total_amount += line.price_subtotal

                    if commission_line:
                        commission_amount = 0
                        if commission_line.use_formula:
                            result = commission_line._run_python_formula(lines=lines, total_amount=total_amount)
                            commission_amount = result
                        elif commission_line.fix_price:
                            commission_amount = commission_line.fix_price
                        else:
                            commission_amount = total_amount * commission_line.percentage / 100
                            if commission_amount < commission_line.minimum_value:
                                commission_amount = commission_line.minimum_value

                        description = product_category.display_name or ''
                        line_vals = {
                            'product_id': commission_product.id,
                            'name': description,
                            'tax_ids': commission_line.tax_ids,
                            'price_unit': commission_amount,
                            'analytic_account_id': purchase.sales_source_id.analytic_account_id,
                        }
                        invoice_vals['invoice_line_ids'].append((0, 0, line_vals))

                if invoice_vals['invoice_line_ids']:
                    move = self.env['account.move'].create(invoice_vals)
                    purchase.commission_invoice_id = move.id

    # For Import
    def _auto_create_bill(self):
        for purchase in self:
            if purchase.so_repair_id or purchase.so_repair_consignee_id or purchase.so_detention_id:
                check_line = all(line.qty_received == line.product_qty for line in purchase.order_line)
                for line in purchase.order_line:
                    line.qty_received = line.product_qty

                if not check_line:
                    purchase.action_create_invoice()

    def _prepare_invoice(self):
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
        invoice_vals['fal_sale_source_id'] = self.sales_source_id.id
        invoice_vals['fal_invoice_mode'] = self.fal_vendor_type
        # invoice_vals['source_job'] = 'import_income' if self.sales_source_id.is_import else 'export_income'
        return invoice_vals

    # For Import
    def _create_repair_invoice(self):
        for purchase in self:
            if purchase.so_repair_id or purchase.so_repair_consignee_id:
                invoice_vals = purchase._fal_prepare_invoice()
                invoice_vals['fal_invoice_mode'] = 'invoice_repair'
                usd = self.env.ref('base.USD')
                if purchase.so_repair_consignee_id:
                    invoice_vals['partner_id'] = purchase.so_repair_consignee_id.partner_id.id
                if purchase.so_repair_id:
                    invoice_vals['currency_id'] = usd.id

                for line in purchase.order_line:
                    line_vals = line._fal_prepare_invoice_line()
                    price_unit = line.price_unit
                    if purchase.so_repair_id:
                        price_unit = line.order_id.currency_id._convert(
                            line.price_unit,
                            usd,
                            line.order_id.company_id,
                            line.order_id.date_order or fields.Date.today()
                        )
                    line_vals['price_unit'] = price_unit
                    invoice_vals['invoice_line_ids'].append((0, 0, line_vals))

                move = self.env['account.move'].create(invoice_vals)
                purchase.repair_invoice_id = move.id

    # For export
    def _create_invoice_commission(self):
        for purchase in self:
            if purchase.partner_id.is_principal and not purchase.so_repair_id and not purchase.sales_source_id.is_import:
                commission_product = purchase.partner_id.product_commission_id
                if not commission_product:
                    raise UserError(_('Please Set Commission Product on Principal: %s')% (purchase.partner_id.name,))

                invoice_vals = purchase._fal_prepare_invoice()
                invoice_vals['partner_id'] = purchase.partner_id.id
                invoice_vals['fal_invoice_mode'] = 'commission'
                invoice_vals['source_job'] = 'import_commission' if self.sales_source_id.is_import else 'export_commission'
                invoice_vals['currency_id'] = self.env.ref('base.USD').id

                commission = self.env['commission.export'].search([
                    ('principal_id', '=', purchase.partner_id.id),
                    ('customer_status', '=', purchase.sales_source_id.customer_status),
                ], limit=1)

                data_category = []
                res = {}
                for line in purchase.order_line:
                    sale_line_id = line.sale_line_id
                    product_set = sale_line_id.product_set_id
                    set_line = product_set.set_line_ids.filtered(lambda a: a.product_id.is_container)
                    product_categ = set_line.product_id.categ_id

                    data_category.append([product_categ, line])

                for key, val in data_category:
                    if key in res:
                        res[key] += [val]
                    else:
                        res[key] = [val]

                for product_category in res:
                    lines = res[product_category]

                    commission_line = commission.commission_line_ids.filtered(lambda a: a.commission_type == 'export' and a.product_category_id.id == product_category.id)
                    total_amount = 0
                    quantity = 0
                    product_desc = ''

                    for line in lines:
                        if line.product_id.id in commission_line.product_ids.ids:
                            product_desc += line.product_id.name + ', '
                            total_amount += line.price_unit
                            quantity = line.product_qty

                    if commission_line:
                        commission_amount = 0
                        if commission_line.use_formula:
                            result = commission_line._run_python_formula(lines=lines, total_amount=total_amount)
                            commission_amount = result
                        elif commission_line.fix_price:
                            commission_amount = commission_line.fix_price
                        else:
                            commission_amount = total_amount * commission_line.percentage / 100
                            if commission_amount < commission_line.minimum_value:
                                commission_amount = commission_line.minimum_value

                        description = product_category.display_name + ': ' + product_desc
                        line_vals = {
                            'product_id': commission_product.id,
                            'name': description or '',
                            'tax_ids': commission_line.tax_ids,
                            'price_unit': commission_amount,
                            'analytic_account_id': purchase.sales_source_id.analytic_account_id,
                            'quantity': quantity
                        }
                        invoice_vals['invoice_line_ids'].append((0, 0, line_vals))

                if invoice_vals['invoice_line_ids']:
                    move = self.env['account.move'].create(invoice_vals)
                    purchase.commission_invoice_id = move.id

    # commision for import
    def _create_invoice_commission_import(self):
        for purchase in self:
            is_ehs = purchase.order_line.filtered(lambda a: a.product_id.is_ehs_comision is True)
            if purchase.partner_id.is_principal and not purchase.so_repair_id and purchase.sales_source_id.is_import and is_ehs:
                commission_product = purchase.partner_id.product_commission_id
                if not commission_product:
                    raise UserError(_('Please Set Commission Product on Principal: %s')% (purchase.partner_id.name,))

                invoice_vals = purchase._fal_prepare_invoice()
                invoice_vals['partner_id'] = purchase.partner_id.id
                invoice_vals['fal_invoice_mode'] = 'commission'
                invoice_vals['source_job'] = 'import_commission'
                invoice_vals['currency_id'] = self.env.ref('base.USD').id

                commission = self.env['commission.export'].search([
                    ('principal_id', '=', purchase.partner_id.id),
                    ('customer_status', '=', purchase.sales_source_id.customer_status),
                ], limit=1)

                data_category = []
                res = {}
                for line in purchase.order_line.filtered(lambda a: a.product_id.is_ehs_comision):
                    sale_line_id = line.sale_line_id
                    product_set = sale_line_id.product_set_id
                    set_line = product_set.set_line_ids.filtered(lambda a: a.product_id.is_ehs_comision)
                    product_categ = set_line.product_id.categ_id

                    data_category.append([product_categ, line])

                for key, val in data_category:
                    if key in res:
                        res[key] += [val]
                    else:
                        res[key] = [val]
                for product_category in res:
                    lines = res[product_category]

                    commission_line = commission.commission_line_ids.filtered(lambda a: a.commission_type == 'import' and product_category.id in a.product_category_id.ids)
                    total_amount = 0
                    quantity = 0
                    product_desc = ''

                    for line in lines:
                        if line.product_id.id in commission_line.product_ids.ids:
                            product_desc += line.product_id.name + ', '
                            total_amount += line.price_unit
                            quantity = line.product_qty

                    if commission_line:
                        commission_amount = 0
                        if commission_line.use_formula:
                            result = commission_line._run_python_formula(lines=lines, total_amount=total_amount)
                            commission_amount = result
                        elif commission_line.fix_price:
                            commission_amount = commission_line.fix_price
                        else:
                            commission_amount = total_amount * commission_line.percentage / 100
                            if commission_amount < commission_line.minimum_value:
                                commission_amount = commission_line.minimum_value

                        description = product_category.display_name + ': ' + product_desc
                        line_vals = {
                            'product_id': commission_product.id,
                            'name': description or '',
                            'tax_ids': commission_line.tax_ids,
                            'price_unit': commission_amount,
                            'analytic_account_id': purchase.sales_source_id.analytic_account_id,
                            'quantity': quantity
                        }
                        invoice_vals['invoice_line_ids'].append((0, 0, line_vals))

                if invoice_vals['invoice_line_ids']:
                    move = self.env['account.move'].create(invoice_vals)
                    purchase.commission_invoice_id = move.id

    def _fal_prepare_invoice(self):
        journal = self.env['account.journal'].search([('company_id', '=', self.company_id.id), ('type', '=', 'sale'), ('operating_unit_id', '=', self.operating_unit_id.id)], limit=1)
        invoice_vals = {
            'partner_id': self.principal_id.id,
            'fal_sale_source_id': self.sales_source_id.id,
            'move_type': 'out_invoice',
            'journal_id': journal and journal.id or False,
            'currency_id': self.currency_id.id,
            'invoice_origin': self.name,
            'company_id': self.company_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'invoice_line_ids': [],
        }
        return invoice_vals

    # For Export
    def _create_invoice_expense(self):
        for purchase in self:
            if purchase.principal_id and not purchase.so_repair_id:
                usd = self.env.ref('base.USD')
                invoice_vals = purchase._fal_prepare_invoice()
                invoice_vals['currency_id'] = usd.id
                invoice_vals['fal_invoice_mode'] = 'expense'

                for line in purchase.order_line:
                    line_vals = line._fal_prepare_invoice_line()
                    if line.order_id.currency_id != usd:
                        price_unit = line.order_id.currency_id._convert(
                            line.price_unit,
                            usd,
                            line.order_id.company_id,
                            line.order_id.date_order or fields.Date.today()
                        )
                        line_vals['price_unit'] = price_unit
                    invoice_vals['invoice_line_ids'].append((0, 0, line_vals))

                move = self.env['account.move'].create(invoice_vals)
                purchase.expense_invoice_id = move.id


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    import_container_info_id = fields.Many2one('import.container.info')
    container_no_id = fields.Many2one('stock.production.lot', string="Container Number")

    def _fal_prepare_invoice_line(self):
        line_vals = {
            'product_id': self.product_id.id,
            'name': self.name,
            'price_unit': self.price_unit,
            'analytic_account_id': self.order_id.sales_source_id.analytic_account_id.id,
            'tax_ids': self.taxes_id,
        }
        return line_vals

    @api.depends('product_id', 'date_order')
    def _compute_account_analytic_id(self):
        res = super(PurchaseOrderLine, self)._compute_account_analytic_id()
        ctx = self.env.context
        for rec in self:
            if ctx.get('analytic_account_id'):
                rec.account_analytic_id = ctx.get('analytic_account_id')
            elif ctx.get('liner_agency'):
                rec.account_analytic_id = self.env.ref('forecastle_module.analytic_account_liner_agency').id
        return res
