# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import datetime
import json as json
from num2words import num2words
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    so_vendor_bill_id = fields.Many2one("sale.order", "Sale Import Vendor Bill", copy=False)

    soa_date = fields.Date(
        string='Soa Date',
        copy=False,
    )

    fal_payment_date = fields.Date(string="fal_payment_date", compute="fal_get_payment_data")
    fal_received_in = fields.Char(string="fal_received_in", compute="fal_get_payment_data")
    fal_amount = fields.Monetary(string="fal_amount", compute="fal_get_payment_data")
    fal_or_name = fields.Char(string="fal_or_name", compute="fal_get_payment_data")

    fal_sale_source_id = fields.Many2one('sale.order', string="Sales Source", copy=False, readonly=True)
    fal_sale_source_id_import = fields.Many2one('sale.order', related='fal_sale_source_id', copy=False, readonly=True)
    source_principal_id = fields.Many2one('res.partner', string="Source Principal", compute="_get_source_principal", store=True)
    is_import = fields.Boolean(string="Is Import", related='fal_sale_source_id.is_import')
    fal_forex = fields.Boolean('Forex', compute='_is_forex')
    fal_rate_currency = fields.Float('Rate Currency')
    fal_rate = fields.Float('Rate')
    fal_total_rate = fields.Float(string='Total Rate', compute='_compute_total_rate')
    source_job = fields.Selection([
        ('export_income', 'Export Income'),
        ('export_commission', 'Export Commission'),
        ('import_income', 'Import Income'),
        ('import_commission', 'Import Commission'),
        ('general_sales', 'General Sales'),
    ], string="Source Job", readonly=True)

    fal_untaxed_amount = fields.Float(string='Untaxed Amount', compute='_compute_total_rate')
    fal_invoice_amount = fields.Float(string='Total', compute='_compute_total_rate')
    fal_invoice_total_taxes = fields.Float(string='Taxes', compute='_compute_total_rate')
    fal_cur_rate = fields.Float(string='Fal Rate Cur', compute='_get_rate')
    fal_cur_rate_warning = fields.Boolean("Rate Warning", compute="_get_rate_warning")
    fal_usd_manual = fields.Boolean(string='USD Manual')
    fal_invoice_type = fields.Selection([
        ('invoice', 'OR Invoice'),
        ('container', 'OR Deposit Container'),
        ('detention', 'OR Deposit Detention'),
    ], string="OR Type", readonly=True)
    fal_invoice_mode = fields.Selection([
        ('invoice', 'Manual Invoice'),
        ('expense', 'Expense Invoice'),
        ('commission', 'Commission Invoice'),
        ('vendor_bill_c2c', 'VB C2C Container'),
        ('vendor_bill_feeder', 'VB Feeder Slot'),
        ('vb_repair', 'VB Repair'),
        ('invoice_repair', 'Invoice Repair'),
    ], string="Invoice Type")

    count_is_dollar = fields.Integer(string='count dollar', compute='_get_count_is_dollar')
    count_is_upsale = fields.Integer(string='count upsale', compute='_get_count_is_upsale')

    upsale_merge = fields.Boolean(string='Upsale Merge')

    @api.onchange('invoice_line_ids')
    def _get_count_is_dollar(self):
        for line in self.invoice_line_ids:
            data = []
            data2 = []
            x = 0
            y = 0
            for record in line.filtered(lambda x: x.product_id.is_dollar and not x.product_id.is_upsale):
                if record:
                    data.append(record.product_id)
                    x = len(data)
                    self.count_is_dollar += x
            for record2 in line.filtered(lambda x: x.product_id.is_upsale):
                if record2:
                    data2.append(record2.product_id)
                    y = len(data2)
                    self.count_is_upsale += y
                else:
                    self.count_is_upsale = 1

    @api.onchange('invoice_line_ids')
    def _get_count_is_upsale(self):
        if self.invoice_line_ids:
            for line in self.invoice_line_ids:
                data2 = []
                y = 0
                if line.product_id.is_upsale:
                    for record2 in line.filtered(lambda x: x.product_id.is_upsale):
                        if record2:
                            data2.append(record2.product_id)
                            y = len(data2)
                            self.count_is_upsale += y
                else:
                    self.count_is_upsale = 1
        else:
            self.count_is_upsale = 1

    def update_cur_rate_price(self):
        self.ensure_one()
        if self.state == 'draft' and self.fal_sale_id and self.fal_sale_id.is_import or self.fal_usd_manual:
            vals = []
            for invoice_line in self.invoice_line_ids.filtered(lambda x: x.fal_sale_price):
                vals.append((1, invoice_line.id, {'price_unit': invoice_line.fal_sale_price * self.fal_cur_rate}))
            self.update({'invoice_line_ids': vals})
        else:
            raise UserError(_('Invoice Is Not in Draft or It is not Import Invoice'))

    @api.onchange('invoice_date')
    def _change_invoice_date(self):
        data = []
        if self.invoice_date:
            for curr in self.currency_id.rate_ids.filtered(lambda x: self.invoice_date >= x.name):
                if curr:
                    data.append(curr.rate)
            for line in self.invoice_line_ids.filtered(lambda x: x.fal_principal_currency_id.name == 'USD'):
                if line.fal_unit_price_usd:
                    line.price_unit = data[0] * line.fal_unit_price_usd

                line.fal_sale_price_quantity = data[0] * line.fal_unit_price_usd

    def _get_rate_warning(self):
        for record in self:
            if any(float_compare(
                    invoice_line.price_unit, invoice_line.fal_sale_price * record.fal_cur_rate, precision_rounding=record.currency_id.rounding
                ) != 0 for invoice_line in record.invoice_line_ids.filtered(lambda x: x.fal_sale_price)):
                record.fal_cur_rate_warning = True
            else:
                record.fal_cur_rate_warning = False

    @api.depends('invoice_date')
    def _get_rate(self):
        for record in self:
            data = []
            record.fal_cur_rate = 0.0
            for line in record.currency_id.rate_ids.filtered(lambda x: record.date >= x.name):
                if line:
                    data.append(line.rate)
                    record.fal_cur_rate = data[0]

    @api.depends('fal_rate_currency')
    def _compute_total_rate(self):
        self.fal_total_rate = False
        self.fal_untaxed_amount = 0.0
        for invoice in self:
            currency_rate_live = 0
            currency_rate_odoo = 0
            price = 0
            total_price_tax = 0
            tax = 0
            test = 0.0
            for move_line in invoice.invoice_line_ids.filtered(lambda x: x.fal_principal_currency_id.symbol == '$' and not x.product_id.is_container and not x.fal_sale_price == 0.0):
                currency_rate_odoo += move_line.price_subtotal
                currency_rate_live += move_line.fal_sale_price * move_line.quantity * invoice.fal_rate_currency
            # for move_line in invoice.invoice_line_ids.filtered(lambda x: x.fal_principal_currency_id.symbol == '$' and not x.product_id.is_container and not x.fal_sale_price == 0.0):
                test = move_line.price_subtotal
            selisih = abs(currency_rate_odoo) - abs(currency_rate_live)
            invoice.fal_total_rate = selisih
            invoice.fal_rate = test
            if invoice.currency_id.symbol == '$':
                for move_line in invoice.invoice_line_ids:
                    compare_rate = move_line.price_unit * move_line.quantity * invoice.fal_total_rate
                    invoice.fal_total_rate = compare_rate - move_line.price_unit
            for untax in invoice.invoice_line_ids:
                # price += untax.fal_transaction_rate
                price += untax.fal_transaction_rate
                total_price_tax  += untax.fal_transaction_total_tax
                tax += untax.fal_transaction_total
            invoice.fal_untaxed_amount = price
            invoice.fal_invoice_amount = total_price_tax
            invoice.fal_invoice_total_taxes = tax

    #compute report or invoice
    def compute_or_invoice(self):
        data_orinv = []
        for x in self.invoice_line_ids.filtered(lambda x: x.product_id.is_container):
            data_orinv.append([x, x.product_id, x.product_uom_qty, x.product_uom.display_name])

        res = {}
        for table, product, uom_qty, uom_name in data_orinv:
            if name in res:
                res[name]['nama'] = name.name
                res[name]['uom_qty'] += qty
            else:
                res[name] = {'nama': name.name, 'uom_qty': qty,}

        container_data_orinv = []
        for record in res:
            container_data_orinv.append(res[record])

        return container_data_orinv

    # @api.depends('fal_rate_currency')
    def get_subtotal_per_column(self):
        total : 0.0
        data_orinv = []
        for x in self.invoice_line_ids.filtered(lambda x: x.product_id.is_container):
            data_orinv.append([x])

        res_orinv = {}
        for name in data_orinv:
            if name in res_orinv:
                res_orinv[name]['total'] = name.price_total
            else:
                res_orinv[name] = {'total': total,}

        container_data_orinv = []
        for record in res_orinv:
            container_data_orinv.append(res_orinv[record])

        return container_data_orinv


    @api.depends('fal_sale_source_id')
    def _get_source_principal(self):
        for inv in self:
            if inv.fal_sale_source_id.is_import:
                inv.source_principal_id = inv.fal_sale_source_id.imp_principal_id.id
            else:
                inv.source_principal_id = inv.fal_sale_source_id.principal_id.id

    @api.depends('invoice_line_ids', 'invoice_line_ids.product_id', 'fal_total_rate')
    def _is_forex(self):
        self.fal_forex = False
        for inv in self:
            forex = inv.invoice_line_ids.product_id.filtered(lambda x: x.is_gain_forex or x.is_loss_forex)
            if forex:
                inv.fal_forex = True

    def generate_forex(self):
        for inv in self:
            if inv.state != 'draft':
                raise UserError(_('Invoice Is Not in Draft'))
            if inv.fal_total_rate >= 0:
                product_gain = self.env['product.product'].search([('is_gain_forex', '=', True), ('company_id', '=', inv.company_id.id)], limit=1)
                tax = self.env['account.tax'].search([('name', '=', 'NIL'), ('company_id', '=', inv.company_id.id), ('type_tax_use', '=', 'sale')], limit=1)
                if not product_gain:
                    raise UserError(_('Product Forex Gain is Not Available For this Company'))
                inv.write({
                    'invoice_line_ids': [(0, 0, {
                        "product_id": product_gain.id,
                        "quantity": 1,
                        "tax_ids": tax,
                        'account_id': product_gain.property_account_income_id.id,
                        "price_unit": inv.fal_total_rate})]
                })
            elif inv.fal_total_rate <= 0:
                product_loss = self.env['product.product'].search([('is_loss_forex', '=', True), ('company_id', '=', inv.company_id.id)], limit=1)
                tax_id = self.env['account.tax'].search([('name', '=', 'NIL'), ('company_id', '=', inv.company_id.id), ('type_tax_use', '=', 'sale')], limit=1)
                if not product_loss:
                    raise UserError(_('Product Forex Loss is Not Available For this Company'))
                inv.write({
                    'invoice_line_ids': [(0, 0, {
                        "product_id": product_loss.id,
                        "quantity": -1,
                        "tax_ids": tax_id,
                        'account_id': product_loss.property_account_income_id.id,
                        "price_unit": inv.fal_total_rate})]
                })

    @api.depends('invoice_payments_widget')
    def fal_get_payment_data(self):
        rdictionary = json.loads(self.invoice_payments_widget)
        if rdictionary:
            for line in rdictionary.get('content'):
                str_amount = line.get('amount')
                str_journal = line.get('journal_name')
                str_date = line.get('date')
                str_nameor = line.get('ref')

                date = datetime.strptime(str_date,'%Y-%m-%d').date()

            self.fal_payment_date = date
            self.fal_received_in = str_journal
            self.fal_amount = str_amount
            self.fal_or_name = str_nameor.split()[0]
        else:
            self.fal_payment_date = False
            self.fal_received_in = False
            self.fal_amount = False
            self.fal_or_name = False

    def action_post(self):
        for move in self:
            if move.date:
                move.soa_date = move.date
        res = super(AccountMove, self).action_post()
        return res

    def get_amount_to_text(self, total_amount):
        return num2words(total_amount)

    ##########################################################
    def compute_invoice_report_not_import(self):
        data = []
        charge_info = self.fal_sale_source_id.charge_info_ids.filtered(lambda a: a.fce_payment_term == 'prepaid')
        for x in self.invoice_line_ids.filtered(lambda a: a.display_type not in ['line_section']):
            check = any(item.product_id.is_container for item in x.product_set_id.set_line_ids)
            check_do_not = x.product_set_id.set_line_ids.filtered(lambda a: a.product_id == x.product_id and a.do_not_merge)
            if not x.product_set_id or not check or x.product_id.is_container or check_do_not:
                data.append(x.id)
        return self.env['account.move.line'].browse(data)
    ##########################################################

    def compute_invoice_report(self):
        data = []
        for record in self.fal_sale_source_id:
            charge_info = record.charge_info_ids.filtered(lambda a: a.fce_payment_term == 'prepaid')
            for x in record.order_line.filtered(lambda a: a.display_type not in ['line_section'] and a.id in charge_info.sale_line_ids.ids):
                check = any(item.product_id.is_container for item in x.product_set_id.set_line_ids)
                check_do_not = x.product_set_id.set_line_ids.filtered(lambda a: a.product_id == x.product_id and a.do_not_merge)
                if not x.product_set_id or not check or x.product_id.is_container or check_do_not:
                    data.append(x.id)
            return record.env['sale.order.line'].browse(data)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    import_container_id = fields.Many2one('import.container.info', string='Container Info Import')
    source_principal_id = fields.Many2one(related='move_id.source_principal_id')
    source_job = fields.Selection(related='move_id.source_job')
    fal_price_tax = fields.Float(string='Price Tax', compute='_compute_amount_invoice')
    fal_sale_price = fields.Float(string='Sale Price')
    fal_sale_price_quantity = fields.Float(string='Sale Price', compute='_compute_sale_price')
    fal_principal_currency_id = fields.Many2one('res.currency', "Currency")
    fal_transaction_rate = fields.Float(string='Transaction Rate', compute='_compute_transaction_rate')
    fal_transaction_total = fields.Float(string='Tax Value', compute='_compute_transaction_rate')
    fal_transaction_total_tax = fields.Float(string='Total')
    fal_system_rate = fields.Float(string='System Rate', compute='_compute_transaction_rate')
    sales_source = fields.Many2one(related='move_id.fal_sale_source_id')
    principal_id = fields.Many2one(related='sales_source.principal_id')
    fal_unit_price_usd = fields.Float(string='Unit Price(USD)')
    fal_currency_medium = fields.Char(string='Field that use as vessel for currency name', compute='_get_currency_name')
    fal_no_container = fields.Char(string='Nomor Kontainer')
    fal_invoice_mode = fields.Selection([
        ('invoice', 'Manual Invoice'),
        ('expense', 'Expense Invoice'),
        ('commission', 'Commission Invoice'),
        ('vendor_bill_c2c', 'VB C2C Container'),
        ('vendor_bill_feeder', 'VB Feeder Slot'),
        ('vb_repair', 'VB Repair'),
        ('invoice_repair', 'Invoice Repair'),
    ], related='move_id.fal_invoice_mode', string="Invoice Type")

    @api.depends('fal_principal_currency_id')
    def _get_currency_name(self):
        for record in self:
            record.fal_currency_medium = ''
            for line in record.fal_principal_currency_id:
                if line:
                    record.fal_currency_medium = line.name


    @api.depends('fal_sale_price', 'quantity', 'price_unit')
    def _compute_transaction_rate(self):
        for line in self:
            line.fal_transaction_rate = line.price_unit * line.quantity
            line.fal_system_rate = line.quantity * line.price_unit
            line.fal_transaction_total = (line.price_unit * (line.tax_ids.amount/100)) * line.quantity
            line.fal_transaction_total_tax = ((line.fal_transaction_rate + line.fal_transaction_total))
            for record in line.filtered(lambda x: x.fal_principal_currency_id.name == 'USD'):
                record.fal_transaction_rate = (record.fal_sale_price*record.move_id.fal_rate_currency) * record.quantity
                record.fal_system_rate = record.price_unit * record.quantity
                record.fal_transaction_total = (record.price_unit * (record.tax_ids.amount/100)) * record.quantity
                record.fal_transaction_total_tax = ((record.fal_transaction_rate + record.fal_transaction_total))
            for gain_loss in line.filtered(lambda x: x.product_id.is_gain_forex or x.product_id.is_loss_forex):
                gain_loss.fal_transaction_rate = 0.0
                gain_loss.fal_transaction_total_tax = ((gain_loss.fal_transaction_rate + gain_loss.fal_transaction_total))

    @api.depends('fal_unit_price_usd')
    def _compute_sale_price(self):
        for line in self:
            line.fal_sale_price_quantity = line.fal_sale_price
            for record in line.filtered(lambda x: x.fal_principal_currency_id.name == 'USD'):
                record.fal_sale_price_quantity = record.fal_unit_price_usd*line.move_id.fal_cur_rate

    @api.onchange('fal_unit_price_usd', 'fal_principal_currency_id')
    def _change_price_unit(self):
        for line in self:
            if line.fal_principal_currency_id.name != 'USD':
                line.fal_unit_price_usd = 0
            line.price_unit = line.fal_sale_price_quantity

    @api.onchange('fal_unit_price_usd')
    def _onchange_fal_sale_price(self):
        for line in self:
            if line.fal_unit_price_usd:
                line.fal_sale_price = line.fal_unit_price_usd

    @api.depends('quantity', 'price_unit', 'tax_ids')
    def _compute_amount_invoice(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.tax_ids.compute_all(
                vals['price_unit'])
            line.update({
                'fal_price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            })

    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the purchase orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency_id': self.move_id.currency_id,
            'quantity': self.quantity,
            'product': self.product_id,
            'partner': self.move_id.partner_id,
        }


class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_contra_account = fields.Boolean(string='Is Contra Account')
