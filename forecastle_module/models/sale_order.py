# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.tools.misc import formatLang, get_lang
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from num2words import num2words
from ast import literal_eval
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_analytic_account(self):
        analytic = self.env.ref('forecastle_module.analytic_account_liner_agency').id
        return analytic

    # Voyage Info
    ofr = fields.Float(string='OFR')
    principal_id = fields.Many2one('res.partner', string="Principal", domain="[('is_principal', '=', True)]")
    vessel_id = fields.Many2one('fce.vessel', string="Vessel ID")
    voyage_id = fields.Many2one('fce.voyage', string="Voyage ID", copy=False)
    connecting_voyage_to_vessel = fields.Many2one('fce.voyage', string=" Conencting Voyage", copy=False)
    connecting_vessel_id = fields.One2many('fce.conves', 'sale_id', string="Connecting Vessel")
    vendor_id = fields.Many2one('res.partner', domain="[('is_vendor', '=', True)]", string="Slot Owner")
    pol_id = fields.Many2one('fce.port.code', string="POL")
    pod_id = fields.Many2one('fce.port.code', string="POD")
    fal_carrier_id = fields.Many2one('res.partner', domain="[('is_carrier', '=', True)]", string="Vessel Operator")
    fal_rate_currency = fields.Float('Rate Currency')
    fal_total_rate = fields.Float(string='Total Rate', compute='_compute_total_rate')
    fal_forex = fields.Boolean('Forex', compute='_is_forex')
    fal_revise_proforma = fields.Boolean('Revise Proforma Invoice', copy=False)
    fal_approve_sale = fields.Boolean('Approve Quotation', copy=False)
    # available_pic_ids = fields.Many2many('res.partner', compute='_get_available_pic's)
    # fal_feeder_pic = fields.Many2one('res.partner', domain="[('id', 'in', available_pic_ids)]", string="Vessel Operator PIC")

    # @api.depends('fal_feeder_pic','partner_id')
    # def _get_available_pic(self):
    #     for line in self:
    #         # quants = line.partner_id.child_ids.filtered(lambda a: a.partner_id == line.partner_id)
    #         _logger.info("________quants___________")
    #         _logger.info(line.child_ids)
    #         lots = quants.mapped('child_ids')
    #         line.available_pic_ids = [(6, 0, lots.ids)]
    available_pic_ids = fields.Many2many('res.partner', compute='_get_available_pic')
    fal_feeder_pic = fields.Many2one('res.partner', domain="[('id', 'in', available_pic_ids)]", string="Vessel Operator PIC")

    count_is_dollar = fields.Integer(string='count dollar', compute='_get_count_is_dollar')
    count_is_upsale = fields.Integer(string='count upsale')

    @api.onchange('order_line')
    def _get_count_is_dollar(self):
        for line in self.charge_info_ids.filtered(lambda a: a.fce_payment_term == 'prepaid'):
            data = []
            data2 = []
            x = 0
            y = 0
            for record in line.sale_line_ids.filtered(lambda x: x.product_id.is_dollar and not x.product_id.is_upsale):
                if record:
                    data.append(record.product_id)
                    x = len(data)
                    self.count_is_dollar += x
            for record2 in line.sale_line_ids.filtered(lambda x: x.product_id.is_upsale):
                if record2:
                    data2.append(record2.product_id)
                    y = len(data2)
                    self.count_is_upsale += y
                else:
                    self.count_is_upsale = 1

    # @api.onchange('invoice_line_ids')
    # def _get_count_is_upsale(self):
    #     if self.invoice_line_ids:
    #         for line in self.invoice_line_ids:
    #             data2 = []
    #             y = 0
    #             if line.product_id.is_upsale:
    #                 for record2 in line.filtered(lambda x: x.product_id.is_upsale):
    #                     if record2:
    #                         data2.append(record2.product_id)
    #                         y = len(data2)
    #                         self.count_is_upsale += y
    #             else:
    #                 self.count_is_upsale = 1
    #     else:
    #         self.count_is_upsale = 1

    def _get_picking_id_items(self):
        data = []
        for record in self.picking_ids.move_line_ids_without_package.filtered(lambda x: x.product_id.is_container):
            data.append([record.product_id, record.qty_done])

        res = {}
        for product, qty in data:
            if product in res:
                res[product]['name'] = product.name
                res[product]['qty'] += qty
            else:
                res[product] = {'name': product.name, 'qty': qty}

        container_product = []
        for record in res:
            container_product.append(res[record])
                
        return container_product

    # ################################################################
    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        res.import_container_info_ids._onchange_container_size_type()
        return res
    # ################################################################

    @api.depends('order_line', 'order_line.product_id', 'fal_total_rate')
    def _is_forex(self):
        self.fal_forex = False
        for sale in self:
            forex = sale.order_line.product_id.filtered(lambda x: x.is_gain_forex or x.is_loss_forex)
            if forex:
                sale.fal_forex = True

    @api.depends('fal_rate_currency', 'order_line', 'order_line.price_unit_principal_currency', 'order_line.product_uom_qty')
    def _compute_total_rate(self):
        self.fal_total_rate = False
        for sale in self:
            currency_rate_live = 0
            currency_rate_odoo = 0
            collect_id = sale.charge_info_ids.search([('fce_payment_term', '=', 'collect')]).sale_line_ids
            not_collect = sale.order_line.filtered(lambda x: x.id not in collect_id.ids)
            for line in not_collect.filtered(lambda x: x.product_id.is_dollar or x.product_id.is_ofr or x.product_id.import_charge and x.price_unit_principal_currency != 0 and x.principal_currency_id.symbol == '$'):
                currency_rate_odoo += line.price_subtotal
                currency_rate_live += line.price_unit_principal_currency * line.product_uom_qty * sale.fal_rate_currency
            selisih = currency_rate_live - currency_rate_odoo
            sale.fal_total_rate = selisih

    def generate_forex(self):
        for sale in self:
            if sale.fal_total_rate >= 0:
                product_gain = self.env['product.product'].search([('is_gain_forex', '=', True), ('company_id', '=', sale.company_id.id)], limit=1)
                tax = self.env['account.tax'].search([('name', '=', 'NIL'), ('company_id', '=', sale.company_id.id), ('type_tax_use', '=', 'sale')], limit=1)
                if not product_gain:
                    raise UserError(_('Product Forex Gain is Not Available For this Company'))
                sale.write({
                    'order_line': [(0, 0, {
                        "product_id": product_gain.id,
                        "product_uom_qty": 1,
                        "tax_id": tax,
                        "price_unit": sale.fal_total_rate})]
                })
            elif sale.fal_total_rate <= 0:
                product_loss = self.env['product.product'].search([('is_loss_forex', '=', True), ('company_id', '=', sale.company_id.id)], limit=1)
                tax_id = self.env['account.tax'].search([('name', '=', 'NIL'), ('company_id', '=', sale.company_id.id), ('type_tax_use', '=', 'sale')], limit=1)
                if not product_loss:
                    raise UserError(_('Product Forex Loss is Not Available For this Company'))
                sale.write({
                    'order_line': [(0, 0, {
                        "product_id": product_loss.id,
                        "product_uom_qty": -1,
                        "tax_id": tax_id,
                        "price_unit": sale.fal_total_rate})]
                })

    def action_approve(self):
        gain_loss_check = self.order_line.filtered(lambda a: a.product_id.is_gain_forex is True or a.product_id.is_loss_forex is True)
        if not gain_loss_check:
            raise UserError('you must generate Gain/Loss before approve')
        elif not self.start_date:
            raise UserError('you must Input Invoice Date')
        else:
            self.fal_approve_sale = True
            if self.is_import:
                self.ensure_one()
                template = self.env.ref('forecastle_module.email_template_send_noa')
                lang = self.env.context.get('lang')
                if template.lang:
                    lang = template._render_lang(self.ids)[self.id]
                ctx = {
                    'default_model': 'sale.order',
                    'default_res_id': self.ids[0],
                    'default_use_template': bool(template.id),
                    'default_template_id': template.id,
                    'default_composition_mode': 'comment',
                    'custom_layout': "mail.mail_notification_paynow",
                    'send_noa': True,
                    'force_email': True,
                    'model_description': self.with_context(lang=lang).type_name,
                }
                return {
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'mail.compose.message',
                    'views': [(False, 'form')],
                    'view_id': False,
                    'target': 'new',
                    'context': ctx,
                }

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        if self.charge_info_ids:
            self.charge_info_ids.unlink()
        return res

    @api.depends('fal_carrier_id', 'fal_carrier_id.child_ids')
    def _get_available_pic(self):
        for line in self:
            child = line.fal_carrier_id.child_ids
            lots = child.mapped('child_ids')
            line.available_pic_ids = [(6, 0, child.ids)]

    agent_id = fields.Many2one('res.partner', string="Agent")
    domain_agent_id = fields.Many2many('fce.agent.code', string="Domain Agent", compute='_get_domain_agent_code')
    # Related Voyage Info
    date_etd = fields.Date(string="ETD", related='voyage_id.date_etd')
    date_eta = fields.Date(string="ETA", related='voyage_id.date_eta')
    re_vessel_id = fields.Many2one(string='Vessel', related='voyage_id.vessel_id')
    re_terminal_code_id = fields.Many2one(string='Terminal Code', related='voyage_id.terminal_id')
    re_carrier_id = fields.Many2one(string='1st Carrier', related='voyage_id.carrier_id')
    etd = fields.Date(string="ETD", related='voyage_id.date_etd')
    eta = fields.Date(string="ETA", related='voyage_id.date_eta')
    date_td = fields.Date(string="Time Departure", related='voyage_id.date_td')
    date_ta = fields.Date(string="Time Arrival", related='voyage_id.date_ta')
    need_connecting_vessel = fields.Boolean(string="Need Connecting Vessel", related="voyage_id.need_connecting_vessel")
    proforma_send = fields.Boolean(string="Proforma Invoice", copy=False)
    proforma_confirmed = fields.Boolean(string="Proforma Invoice Confirmed", copy=False)
    proforma_filename = fields.Char(string="Proforma Filename", copy=False)
    proforma_file = fields.Binary(string="Proforma Invoice File", copy=False)
    fal_total_receipt = fields.Float(string="Total Receipt Angka", required=False, compute="amount_to_word")
    fal_total_amount = fields.Float(string="Total A",required=False, compute="amount_to_word")
    fal_receipt = fields.Char(string="Total Receipt Word",required=False, compute="amount_to_word_container")
    fal_amount_text = fields.Char(string="Total Amount Word Invoice",required=False, compute="amount_to_word_invoice")
    fal_receipt_det = fields.Char(string="Total Amount Word Detention",required=False, compute="amount_to_word_detention")
    fal_receipt_inv = fields.Char(string="Total Amount Word Invoice",required=False, compute="amount_to_word_or_invoice")
    # Flat File
    package_code_id = fields.Many2one('fce.package.code', string="Package Code", copy=False)
    group_code_id = fields.Many2one('fce.group.code', string="Group Code", copy=False)
    kpbc_code_id = fields.Many2one('fce.kpbc.code', string="KPBC Code", copy=False)
    depot_name_id = fields.Many2one('stock.location', string="Depot Name", domain="[('usage', '!=', 'view')]", copy=False)
    unit = fields.Integer('Unit', copy=False)
    code_flat_file = fields.Char('Code Flat File', compute='_codeflatfile')
    analytic_account_id = fields.Many2one(default=_get_analytic_account)
    flat_date_td = fields.Char('Flat Date TD', compute='tes_flat_date_td')
    flat_bl_issue_date = fields.Char('Flat Bl Issue Date', compute='code_flat_bl_issue_date')
    flat_peb_date = fields.Char('Flat Peb Date', compute='code_flat_peb_date')
    flat_sequence = fields.Char('Flat Sequence')
    flat_vessel_name = fields.Char('Flat Vessel Name', size=52, compute='_codevesselname')
    flat_voyage_name = fields.Char('Flat Voyage Name', size=34, compute='_codevoyagename')
    flat_pol_pod_name = fields.Char('Pol Pod Name', size=70, compute='_polpodname')
    flat_bl_number = fields.Char('Bl Number Report', size=30, compute='_flatblnumber')
    container_load = fields.Selection([
        ('E', 'E'),
        ('F', 'F'),
    ])
    agent_code_id = fields.Many2one('fce.agent.code', string="Agent Code")
    load_date = fields.Date(string="Loading Date", copy=False)
    gate_cy_date = fields.Date(string="Gate In CY", copy=False)
    start_date_sales = fields.Date(string="Start Date")

    def _flatblnumber(self):
        self.flat_bl_number = False
        for x in self:
            bl = x.bl_number
            if bl:
                bl_total = 30
                bl_length = len(bl)
                if bl_length <= 30:
                    for i in range(bl_total - bl_length):
                        bl += ' '
            else:
                bl_length = 0
                x.flat_bl_number = ''
            x.flat_bl_number = bl

    @api.depends('pol_id', 'pod_id')
    def _polpodname(self):
        self.flat_pol_pod_name = False
        for x in self:
            pol_pod_name = x.pol_id.name + x.pol_id.name + x.pod_id.name + x.pod_id.name + x.re_vessel_id.name
            if pol_pod_name:
                pol_pod_total = 70
                pol_pod_length = len(pol_pod_name)
                if pol_pod_length <= 70:
                    for i in range(pol_pod_total - pol_pod_length):
                        pol_pod_name += ' '
            else:
                pol_pod_length = 0
                x.flat_pol_pod_name = ''
            x.flat_pol_pod_name = pol_pod_name

    @api.depends('re_vessel_id', 're_vessel_id.name')
    def _codevesselname(self):
        self.flat_vessel_name = False
        for x in self:
            vessel_name = x.re_vessel_id.name
            if vessel_name:
                vessel_total = 52
                vessel_length = len(x.re_vessel_id.name)
                if vessel_length <= 52:
                    for i in range(vessel_total - vessel_length):
                        vessel_name += ' '
            else:
                vessel_length = 0
                x.flat_vessel_name = ''
            x.flat_vessel_name = vessel_name

    @api.depends('voyage_id', 'voyage_id.name')
    def _codevoyagename(self):
        self.flat_voyage_name = False
        for x in self:
            voyage_name = x.voyage_id.name
            if voyage_name:
                voyage_total = 34
                voyage_length = len(x.re_vessel_id.name)
                if voyage_length <= 34:
                    for i in range(voyage_total - voyage_length):
                        voyage_name += ' '
            else:
                x.flat_voyage_name = ''
            x.flat_voyage_name = voyage_name

    @api.onchange('start_date_sales')
    def onchange_start_date_sales(self):
        for record in self:
            if record.start_date_sales:
                record.date_order = record.start_date_sales

    @api.onchange('agent_code_id')
    def _get_agent_code(self):
        for record in self:
            if record.agent_code_id:
                self.agent_id = record.agent_code_id.agent_id.id

    @api.depends('principal_id')
    def _get_domain_agent_code(self):
        self.domain_agent_id = False
        for record in self:
            if record.principal_id:
                self.domain_agent_id = record.principal_id.fal_agent_code_ids.ids
            else:
                self.domain_agent_id = False

    @api.onchange('connecting_voyage_to_vessel')
    def _connecting_vessel(self):
        self.connecting_vessel_id = False
        values = []
        if self.connecting_voyage_to_vessel:
            for poc in self.connecting_voyage_to_vessel.port_of_call_ids:
                values.append((0, 0, {
                        'port_code_id': poc.port_code_id.id,
                        'port_type': poc.port_type,
                        'voyage_id': self.voyage_id.id,
                        'vessel_id': self.connecting_voyage_to_vessel.vessel_id.id,
                        'date_etd': poc.date_etd,
                        'date_eta': poc.date_eta
                }))
        self.connecting_vessel_id = values

    def compute_proforma_invoice_report(self):
        data = []
        # line = self.order_line.filtered()
        charge_info = self.charge_info_ids.filtered(lambda a: a.fce_payment_term == 'prepaid')
        for x in self.order_line.filtered(lambda a: a.display_type not in ['line_section'] and a.id in charge_info.sale_line_ids.ids):
            check = any(item.product_id.is_container for item in x.product_set_id.set_line_ids)
            check_do_not = x.product_set_id.set_line_ids.filtered(lambda a: a.product_id == x.product_id and a.do_not_merge)
            if not x.product_set_id or not check or x.product_id.is_container or check_do_not:
                data.append(x.id)
        return self.env['sale.order.line'].browse(data)

    @api.onchange('depot_name_id')
    def _check_available_quantity_location(self):
        warning = ''
        if self.depot_name_id:
            for line in self.order_line.filtered(lambda a: a.product_id.is_container):
                quants = line.product_id.stock_quant_ids.filtered(lambda a: a.location_id == self.depot_name_id)
                qty_available = sum(quant.quantity for quant in quants)
                if line.product_uom_qty > qty_available:
                    warning += '\n Jumlah Stock Kontainer %s = %s  tidak sesuai dengan jumlah booking' % (line.product_id.name, str(qty_available))

            if warning:
                raise UserError(_(warning))

    @api.depends('cro_ids.measure', 'cro_ids.gross', 'package_code_id', 'unit')
    def _codeflatfile(self):
        for x in self:
            gross_code = ''
            gross_total = sum(float(m.gross) for m in x.cro_ids)
            gross_length = 14 - len(str(float(gross_total)))
            for i_gross in range(gross_length):
                gross_code += '0'
            gross_code += str(float(gross_total))

            measure_code = ''
            measure_total = sum(float(m.measure) for m in x.cro_ids)
            measure_length = 18 - len(str(float(measure_total)))
            for i in range(measure_length):
                measure_code += '0'
            measure_code += str(float(measure_total))

            require = ''
            require_total = len(x.cro_ids.ids)
            require_length = 9 - len(x.cro_ids.ids)
            for i in range(require_length):
                require += '0'
            require += str(int(require_total))

            unit_code = ''
            unit_total = x.unit
            unit_length = 8 - len(str(int(unit_total)))
            for i in range(unit_length):
                unit_code += '0'
            unit_code += str(int(unit_total))

            package_code = ''
            code_length = 28 - len(str(x.package_code_id.code))
            for i in range(code_length):
                package_code += '0'
            package_code += str(x.package_code_id.code)
            x.code_flat_file = gross_code + measure_code + require + unit_code + package_code

    def write(self, values):
        if values.get('cro_ids'):
            code = 0
            for i in self.cro_ids:
                code += 1
                code_sequence = '%0*d' % (4, code)
                i.code_sequence = code_sequence
        if self.charge_info_ids:
            for sale in self:
                for x in sale.charge_info_ids:
                    if not x.sale_line_ids:
                        x.unlink()
        return super(SaleOrder, self).write(values)

    @api.depends('date_td')
    def tes_flat_date_td(self):
        for dt in self:
            int_date = dt.date_td
            if int_date:
                dt.flat_date_td = int_date.strftime('%Y%m%d')
            else:
                dt.flat_date_td = 0

    @api.depends('bl_issue_date')
    def code_flat_bl_issue_date(self):
        for dt in self:
            int_date = dt.bl_issue_date
            if int_date:
                dt.flat_bl_issue_date = int_date.strftime('%Y%m%d')
            else:
                dt.flat_bl_issue_date = 0

    @api.depends('bl_issue_date')
    def code_flat_peb_date(self):
        for dt in self:
            int_date = dt.peb_date
            if int_date:
                dt.flat_peb_date = int_date.strftime('%Y%m%d')
            else:
                dt.flat_peb_date = 0

    #compute report container deposit
    def compute_import_container_report(self):
        data_cont = []
        for x in self.import_container_info_ids:
            data_cont.append([x.product_id, x.con_deposit, x.quantity, x.last_date])

        res_cont = {}
        for name, price_cont, qty, ex_date in data_cont:
            if name in res_cont:
                res_cont[name]['nama'] = name.name
                res_cont[name]['uom_qty'] += qty
                res_cont[name]['price_cont'] = price_cont
                res_cont[name]['ex_date'] = ex_date
            else:
                res_cont[name] = {'nama': name.name, 'uom_qty': qty, 'price_cont': price_cont, 'ex_date': ex_date}

        container_data_cont = []
        for record in res_cont:
            container_data_cont.append(res_cont[record])

        return container_data_cont

    #compute report detention deposit
    def compute_import_detention_report(self):
        data_det = []
        for x in self.import_container_info_ids:
            data_det.append([x.product_id, x.total_detention_deposit, x.quantity])

        res_det = {}
        for name, price_det, qty in data_det:
            if name in res_det:
                res_det[name]['nama'] = name.name
                res_det[name]['uom_qty'] += qty
                res_det[name]['price_det'] = price_det
            else:
                res_det[name] = {'nama': name.name, 'uom_qty': qty, 'price_det': price_det}

        container_data_det = []
        for record in res_det:
            container_data_det.append(res_det[record])

        return container_data_det

    # nominal currency to word report invoice
    # @api.depends('order_line', 'order_line.fal_total_incl_ppn')
    def amount_to_word_invoice(self):
        x = 0
        y = 0
        z = 0
        self.fal_amount_text = ''
        # for line in self.order_line.filtered(lambda x: x.product_id.is_gain_forex or x.product_id.is_loss_forex):
        #     if line:
        #         z += line.price_unit
        for record in self.charge_info_ids.filtered(lambda a: a.fce_payment_term == 'prepaid'):
            # for line in self.order_line.filtered(lambda b: record.sale_line_ids.name == b.product_id.name):
            #     x += line.price_total
            for line in record.sale_line_ids:
                x += line.price_total
        self.fal_amount_text = num2words(x)



    # nominal currency to word report official receipt invoice
    @api.depends('order_line', 'order_line.total_by_product_set')
    def amount_to_word_or_invoice(self):
        for sale_order in self:
            amount_inv = 0.0
            for line in sale_order.order_line.filtered(lambda x: x.product_id.is_container):
                j=0.0
                for line2 in sale_order.order_line.filtered(lambda x: x.product_set_id == line.product_set_id and x.display_type == 'line_section'):
                    amount_inv += line2.total_by_product_set

            sale_order.fal_receipt_inv = num2words(amount_inv)

    # nominal currency to word report official receipt container deposit
    def amount_to_word_container(self):
        for sale_order in self:
            amount=0.0
            data = sale_order.compute_import_report()
            for line in data:
                amount+=line.get('price')*line.get('uom_qty')
            sale_order.fal_receipt = num2words(amount)

    #nominal currency to word report official receipt detention deposit
    def amount_to_word_detention(self):
        for sale_order in self:
            amount = 0.0
            for line in sale_order.import_container_info_ids:
                amount += line.total_detention_deposit
            sale_order.fal_receipt_det = num2words(amount)

    # Booking Info
    booking_type = fields.Selection([
        ('la', 'Linear Agency'),
        ('nvocc', 'NVOCC'),
    ])
    start_date = fields.Date(string=" Start Date")
    validity_date = fields.Date(string="Expiry Date", copy=True)

    pricelist_id = fields.Many2one(required=False)
    booking_estimation_date = fields.Date(string="Booking Estimation")
    bl_number = fields.Char("BL Number", copy=False)
    bl_issue = fields.Selection([
        ('seawaybill', 'Seawaybill'),
        ('surendered', 'Surendered'),
        ('original', 'Original'),
    ], string="BL Issue", copy=False)

    freight = fields.Selection([
        ('prepaid', 'Prepaid'),
        ('collect', 'Collect'),
    ], string="Freight", copy=False)

    fal_container_type = fields.Selection([
        ('soc', 'SOC'),
        ('coc', 'COC'),
    ], string="Container", copy=False)

    term = fields.Selection([
        ('cycy', 'CY-CY'),
        ('cyfo', 'CY-FO'),
    ], string="Term", compute='_get_term', copy=False)

    def _get_term(self):
        for rec in self:
            if rec.connecting_vessel_id:
                self.term = 'cyfo'
            else:
                self.term = 'cycy'

    # Surat tugas
    fal_nama_pemberi_tugas = fields.Many2one('hr.employee', string='Nama Pemberi Tugas')
    fal_alamat_pemberi_tugas = fields.Char(string='Alamat Pemberi Tugas')
    fal_jabatan_pemberi_tugas = fields.Char(string='Jabatan Pemberi Tugas')

    fal_nama_penerima_tugas = fields.Many2one('hr.employee', string='Nama Penerima Tugas')
    fal_alamat_penerima_tugas = fields.Char(string='Alamat Penerima Tugas')
    fal_jabatan_penerima_tugas = fields.Char(string='Jabatan Penerima Tugas')
    temp_no_container = fields.Char(string='No Kontainer')

    def _get_country(self):
        country = self.env.ref('base.id')
        return [('country_id', '=', country.id)]

    @api.onchange('voyage_id')
    def _get_atd_etd(self):
        self.bl_issue_date = ''
        for record in self.voyage_id:
            for x in record.port_of_call_ids.filtered(lambda z: z.port_type == 'pol'):
                self.bl_issue_date = x.date_etd
                if x.date_td:
                    self.bl_issue_date = x.date_td

    @api.onchange('pol_id')
    def _get_pol_state(self):
        self.bl_issue_place = ''
        for record in self:
            record.bl_issue_place = record.pol_id.state_id

    bl_issue_place = fields.Many2one('res.country.state', string="BL Issue Location", domain=_get_country, compute='_get_pol_state')
    bl_issue_date = fields.Date("BL Issue Date", compute='_get_atd_etd', copy=False)
    agent_id = fields.Many2one('res.partner',)
    # shipping instruction

    # def _default_shipper_id(self):
    #     booking_party= self.env.context.get('partner_id')
    #     return self.env['res.partner'].search([('id', '=',booking_party )])

    shipper_id = fields.Many2one('res.partner', domain="[('is_shipper', '=', True)]", string="Shipper", copy=False)
    shipper_address = fields.Text(string="Shipper Address", copy=False)

    consignee_id = fields.Many2one('res.partner', domain="[('is_consignee', '=', True)]", string="Consignee", copy=False)
    consignee_address = fields.Text(string="Consignee Address", copy=False)

    notify_id = fields.Many2one('res.partner', domain="[('is_norify', '=', True)]", string="Notify", copy=False)
    notify_address = fields.Text(string="Notify Address", copy=False)
    # Container Info
    container_qty = fields.Integer(string="Quantity")
    container_type_id = fields.Many2one('product.template', string="Container Type")
    container_no = fields.Char(string="Container No.")
    gross_weight = fields.Char(string="Gross Weight")
    net_weight = fields.Char(string="Net Weight")
    measure = fields.Char(string="Measure")
    commodity = fields.Char(string="Commodity")
    # HS Code & Incoterm
    international_term = fields.Many2one('account.incoterms', string="Inco Term")
    peb_no = fields.Char(string="PEB No.", copy=False)
    peb_date = fields.Date(string="PEB Date", copy=False)
    kppbc = fields.Date(string="KPPBC", copy=False)
    hs_code = fields.Char(string="HS Code")
    good_description = fields.Text(string="Description of Goods", copy=False)
    remarks = fields.Text(string="Remarks", copy=False)
    detention = fields.Char(string="Detention")
    fce_disclaimer = fields.Char(string="Disclaimer.")
    # Change State & Naming
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Booking Confirmed'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    booking = fields.Boolean("Booking", default=False, copy=False)
    surendered = fields.Boolean("Surendered", default=False, copy=False)
    internal_confirm = fields.Boolean("Internal Confirm", default=False, copy=False)
    seawaybill = fields.Boolean("Seawaybill", default=False, copy=False)
    booking_email_send = fields.Boolean("Booking Email", default=False, copy=False)
    final_si = fields.Boolean("Final SI", default=False, copy=False)
    confirmed_draft_bl = fields.Boolean("Confirmed Draft BL", default=False, copy=False)
    unit_price_markdown = fields.Boolean("Unit Price Mark-down", compute="_get_unit_price_markdown")
    # Invoicing
    fce_payment_term = fields.Selection([
        ('prepaid', 'Prepaid'),
        ('collect', 'Collect'),
    ])

    fal_signature_selection = fields.Selection([
        ('signature', 'Signature'),
        ('nothing', 'No Signature'),
    ], string='Signature Options', copy=False, default='signature')
    charge_info_ids = fields.One2many('charge.info', 'sale_id', string="Charge Info", copy=False)
    # Margin
    has_lower_than_mrg = fields.Boolean('Warning: Price Lower than MRG', compute="_get_warning_mrg", store=True)
    # CRO
    cro_ids = fields.One2many("fce.cro", 'sale_order_id', 'Container Release Order', copy=False)
    # Feeder Purchase
    po_feeder_ids = fields.One2many('purchase.order', 'so_id', "Feeder Purchase Order's")
    invoice_get_ids = fields.One2many('account.move', 'fal_sale_source_id', 'Invoice ID Gets')
    po_feeder_count = fields.Integer(compute='_compute_purchase_order_feeder_count', string='Feeder Purchase Order Count')
    invoice_count_field = fields.Integer(compute='_compute_invoice_count', string='Invoice Order Count')

    def _compute_invoice_count(self):
        self.invoice_count_field = len(self.invoice_get_ids)

    def get_current_name(self):
        for x in self:
            x.telex_validate = self.env.user.id

    telex_validate = fields.Many2one('res.users', string='Telex Validate By', copy=False)

    fal_selection_status = fields.Selection([
        ('pending', 'Pending'),
        ('revise', 'Revise'),
        ('confirm', 'Confirm'),
        ('reject', 'Reject'),
    ], string='Selection Status')

    fal_route = fields.Char('Route')

    fal_get_user = fields.Char(string="User", compute="_get_self_user")
    fal_get_division = fields.Char(string="Division", compute="_get_self_user")

    def action_change_start_date(self):
        self.date_order = self.start_date
        gain_loss_check = self.order_line.filtered(lambda a: a.product_id.is_gain_forex is True or a.product_id.is_loss_forex is True)
        if gain_loss_check:
            raise UserError('Please Delete Gain/Loss Forex product in Sale Order Lines before change Invoice Date"')
        else:
            for sale_line in self.order_line:
                sale_line.with_context(product_set=sale_line.product_set_id).product_id_change()

    def _get_self_user(self):
        self.fal_get_user = self.env.user.employee_id.name
        self.fal_get_division = self.env.user.employee_id.department_id.name

    # Commission
    customer_status = fields.Selection([
        ('general', 'General'),
        ('inhouse', 'Inhouse'),
        ('nomination', 'Nomination'),
    ], string="Customer Status", default='general')

    # Generate BL number
    def action_generate_bl_number(self):
        for sale in self:
            seq_obj = self.env['ir.sequence']
            seq = seq_obj.next_by_code('seq.bl.number') or '/'
            if sale.principal_id.initial_bl and not sale.bl_number:
                sale.bl_number = sale.principal_id.initial_bl + sale.operating_unit_id.forecastle_code + seq

    @api.onchange('voyage_id')
    def _onchange_voyage(self):
        self.bl_issue_date = self.etd

    def _compute_purchase_order_feeder_count(self):
        self.po_feeder_count = len(self.po_feeder_ids)

    def action_view_feeder_purchase_orders(self):
        self.ensure_one()
        purchase_order_ids = self.po_feeder_ids.ids
        action = {
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
        }
        action.update({
            'name': _("Feeder Purchase Order generated from %s", self.name),
            'domain': [('id', 'in', purchase_order_ids)],
            'view_mode': 'tree,form',
            'context': {
                'analytic_account_id': self.analytic_account_id.id,
                'default_sales_source_id': self.id,
                'default_so_id': self.id,
                'default_principal_id': self.principal_id and self.principal_id.id,
            }
        })
        return action

    def action_view_invoices(self):
        self.ensure_one()
        invoice_order_ids = self.invoice_get_ids.ids
        action = {
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
        }
        action.update({
            'name': _("Invoice from %s", self.name),
            'domain': [('id', 'in', invoice_order_ids)],
            'view_mode': 'tree,form,kanban',
            'context': {
                'analytic_account_id': self.analytic_account_id.id,
                'default_sales_source_id': self.id,
                'default_fal_sale_source_id': self.id,
                'default_principal_id': self.principal_id and self.principal_id.id,
                'default_move_type': 'out_invoice',
            }
        })
        return action

    def action_revise_bl(self):
        for sale in self:
            sale.confirmed_draft_bl = False

    def action_surender(self):
        SaleOrderLine = self.env['sale.order.line']
        for sale in self:
            product_id = self.env['product.product'].search([('product_tmpl_id.is_telex', '=', True)], limit=1)
            if not product_id:
                raise UserError(_("No Product Telex, Please set on Product"))

            values = {
                'order_id': sale.id,
                'product_uom_qty': 1,
                'product_uom': product_id.uom_id.id,
                'product_id': product_id.id,
            }
            SaleOrderLine.sudo().create(values)
            if sale.invoice_ids and not sale.surendered:
                sale._create_invoice_telex()
            sale.surendered = True

    def action_internal_confirm(self):
        for sale in self:
            sale.internal_confirm = True
            sale.action_confirm()
            sale.create_charge_info()
            # sale.check_charge_info()

    def create_charge_info(self):
        for sale in self:
            sale.charge_info_ids = False
            values = [(6, 0, [])]
            for line in sale.order_line.filtered(lambda x: x.do_not_merge or not x.product_set_id or x.display_type in ['line_section', 'line_note'] and x.total_by_product_set):
                sale_line_ids = line
                if not line.product_id:
                    sale_line_ids = sale.order_line.filtered(lambda x: x.product_set_id == line.product_set_id and not x.do_not_merge)

                values.append((0, 0, {
                    'name': line.product_id.name,
                    'bill_to_id': sale.partner_id.id,
                    'fce_payment_term': 'prepaid',
                    'sale_line_ids': [(6, 0, sale_line_ids.ids)],
                }))
            sale.charge_info_ids = values

    def action_confirm(self):
        for sale in self:
            for line in sale.order_line.filtered(lambda x: x.product_id.is_container):
                new_quantity = len(sale.cro_ids.filtered(lambda a: a.container_type_id == line.product_id and a.container_categ == 'coc'))
                line.product_uom_qty = new_quantity
        res = super(SaleOrder, self).action_confirm()
        # self._auto_create_invoice()
        self._auto_set_container_number()
        return res

    def _auto_set_container_number(self):
        for sale in self:
            # move_line_lot_set = []
            # for container in sale.cro_ids:
            #     # lot1
            #     move_lines = self.env['stock.move.line'].search([('id', 'not in', move_line_lot_set), ('move_id.sale_line_id', '=', container.sale_line_id.id)])
            #     for line in move_lines:
            #         if line.id not in move_line_lot_set:
            #             line.lot_id = container.container_number_id.id
            #             move_line_lot_set.append(line.id)
            #             break
            if sale.depot_name_id:
                for pick in sale.picking_ids:
                    pick.write({'location_id': sale.depot_name_id.id,})
                    pick.move_line_ids_without_package.sudo().write({'location_id': sale.depot_name_id.id, 'pod_id': sale.pod_id.id,'loading_date': sale.load_date,'gate_in_cy': sale.gate_cy_date})

            for pick in sale.picking_ids:
                for line in pick.move_line_ids_without_package:
                    line.lot_id = False

    def _check_shipper(self):
        for sale in self:
            if not sale.is_import:
                message = 'Shipper'
                if not sale.shipper_id:
                    raise UserError(_("%s is Empty") % message)

    def _check_consignee_notify(self):
        for sale in self:
            if not sale.is_import:
                message = ''
                if not sale.consignee_id or not sale.notify_id:
                    if not sale.consignee_id:
                        message += 'Consignee, '

                    if not sale.notify_id:
                        message += 'Notify, '

                    raise UserError(_("%s is Empty") % message)

    def _check_peb(self):
        for sale in self:
            if not sale.is_import:
                message = ''
                if not sale.peb_no or not sale.peb_date or not sale.kpbc_code_id or not sale.good_description:
                    if not sale.peb_no:
                        message += 'Peb Number, '
                    if not sale.peb_date:
                        message += 'Peb Date, '
                    if not sale.kpbc_code_id:
                        message += 'KPPBC, '
                    if not sale.good_description:
                        message += 'Description, '
                    raise UserError(_("%s is Empty") % message)

    def _check_gross_weight_container(self):
        for sale in self:
            if not sale.is_import:
                message = ''
                for cro in sale.cro_ids:
                    if not cro or not cro.gross or not cro.nett:
                        if not cro:
                            message += 'Container, '
                        if not cro.gross:
                            message += 'Gross, '
                        if not cro.nett:
                            message += 'Net Weight, '
                        raise UserError(_("%s is Empty") % message)

    def _check_hs_code(self):
        for sale in self:
            if not sale.is_import:
                message = ''
                if not sale.cro_ids or not sale.cro_ids.hs_code:
                    if not sale.cro_ids.hs_code:
                        message += 'Hs Code, '
                    raise UserError(_("%s is Empty") % message)

    def _check_validate_delivery(self):
        for order_line in self.order_line.filtered(lambda a: a.product_id.is_container):
            if not order_line.qty_delivered > 0:
                raise UserError('Please Confirm Your Delivered First')

    # Override odoo method
    def _get_invoiceable_lines(self, final=False):
        """Return the invoiceable lines for order `self`."""
        down_payment_line_ids = []
        invoiceable_line_ids = []
        pending_section = None
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        charge_info = self.charge_info_ids.filtered(lambda a: a.fce_payment_term == 'prepaid')
        lines = charge_info.mapped('sale_line_ids')
        line_order = self.order_line
        if self.is_import:
            line_order = self.order_line
        else:
            line_order = self.order_line.filtered(lambda l: l.id in lines.ids or not l.product_id)
        for line in line_order:
            if line.display_type == 'line_section':
                # Only invoice the section if one of its lines is invoiceable
                pending_section = line
                continue
            if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                continue
            if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                if line.is_downpayment:
                    # Keep down payment lines separately, to put them together
                    # at the end of the invoice, in a specific dedicated section.
                    down_payment_line_ids.append(line.id)
                    continue
                if pending_section and line.product_set_id and not line.do_not_merge:
                    invoiceable_line_ids.append(pending_section.id)
                    pending_section = None
                invoiceable_line_ids.append(line.id)
        return self.env['sale.order.line'].browse(invoiceable_line_ids + down_payment_line_ids)

    def _generate_wizard_invoice(self):
        advance_wizard_obj = self.env['sale.advance.payment.inv']
        advPmnt = advance_wizard_obj.create({'advance_payment_method': 'delivered'})
        advPmnt.with_context({'default_journal_id': self._context.get('default_journal_id', False), 'active_ids': self.ids}).create_invoices()

    def _create_invoice_telex(self):
        for sale in self:
            telex = sale.order_line.filtered(lambda a: a.product_id.is_telex)
            if telex:
                telex.write({'qty_delivered': telex.product_uom_qty})
                sale.with_context({'default_journal_id': telex.order_id.invoice_ids.journal_id.id or False, 'active_ids': self.ids})._generate_wizard_invoice()

    def _auto_create_invoice(self):

        for sale in self:
            group_by_partner = []
            for charge in sale.charge_info_ids.filtered(lambda a: a.fce_payment_term == 'prepaid'):
                partner = charge.bill_to_id
                if not partner:
                    partner = sale.partner_id

                group_by_partner.append((partner, charge))

            res = {}
            for key, val in group_by_partner:
                if key in res:
                    res[key] += [val]
                else:
                    res[key] = [val]

            # Make qty 0 first for container
            for line in sale.order_line.filtered(lambda a: a.product_id.is_container):
                line.write({'qty_delivered': 0})

            for partner in res:
                for charge_info in res[partner]:
                    for line in charge_info.sale_line_ids.filtered(lambda a: a.product_id):
                        line.write({'qty_delivered': line.product_uom_qty})

                sale._generate_wizard_invoice()

                for charge_info in res[partner]:
                    # Write Bill to, to invoice
                    for line in charge_info.sale_line_ids.filtered(lambda a: a.product_id):
                        inv_line = line.invoice_lines
                        inv_line.move_id.write({'partner_id': partner.id})


    @api.depends('order_line', 'order_line.price_unit')
    def _get_unit_price_markdown(self):
        for sale in self:
            if any(line.price_unit < line.initial_price for line in sale.order_line):
                sale.unit_price_markdown = True
            else:
                sale.unit_price_markdown = False

    #########################################
    # OnChange Logic
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        """
        if not self.partner_id:
            self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
                'fiscal_position_id': False,
            })
            return

        self = self.with_company(self.company_id)

        super(SaleOrder, self).onchange_partner_id()
        values = {}
        values['pricelist_id'] = self._get_mrg_pricelist() or False
        values['shipper_id'] = self.partner_id or False
        self.update(values)

    @api.model
    def get_hs_code(self, modalcontainerinfo_hs):
        hs_code = self.env['fce.hs.code'].search([('id', '=', modalcontainerinfo_hs)])
        hsc = []
        if hs_code:
            for hs in hs_code:
                hsc.append(hs.name)
        return hsc

    @api.onchange('pol_id')
    def _onchange_pol_id(self):
        if self.pol_id:
            self.bl_issue_place = self.pol_id.state_id.id

    @api.onchange('principal_id', 'fal_carrier_id', 'pol_id', 'pod_id', 'validity_date', 'start_date_sales', 'partner_id')
    def get_pricelist_id(self):
        """
        Update the following fields when the pricelist component is changed:
        - Pricelist
        """
        self.update({'pricelist_id': self._get_mrg_pricelist()})
        res = {}
        res['domain'] = {'agent_code_id': [('id', 'in', self.principal_id.fal_agent_code_ids.ids)]}
        return res

    def _get_mrg_pricelist(self):
        if self.is_import:
            currency_id = self.env.ref('base.IDR')
            pricelist = self.env['product.pricelist'].search([('name', '=', 'IMPORT LOCAL CHARGES'), ('currency_id', '=', currency_id.id)], limit=1)
            if pricelist:
                return pricelist.id
            else:
                return False
        else:
            if self.company_id and self.pol_id and self.pod_id and self.validity_date and self.start_date_sales:
                pricelist_id = self.env['product.pricelist'].search([('company_id', '=', self.company_id.id), ('principal_id', '=', self.principal_id.id), '|', ('partner_id', '=', self.partner_id.id), ('partner_id', '=', False), '|', ('carrier_id', '=', self.fal_carrier_id.id), ('carrier_id', '=', False), ('pol_id', '=', self.pol_id.id), ('pod_id', '=', self.pod_id.id), ('start_date', '<=', self.start_date_sales), ('date_validity', '>=', self.validity_date), ('currency_id', '=', self.env.ref('base.IDR').id)], limit=1)
                if pricelist_id:
                    return pricelist_id.id
                else:
                    return False
            else:
                return False

    ################################################
    # Compute Logic
    @api.depends('order_line', 'pricelist_id', 'order_line.initial_price')
    def _get_warning_mrg(self):
        for so in self:
            if any(soline.initial_price > soline.price_unit for soline in so.order_line):
                so.has_lower_than_mrg = True
            else:
                so.has_lower_than_mrg = False

    ################################################
    # CRO Logic
    def create_cro_lines(self):
        values = [(6, 0, [])]
        for line in self.order_line.filtered(lambda x: x.product_id.is_container):
            for i in range(int(line.product_uom_qty)):
                values.append((0, 0, {
                    'sequence': i,
                    'container_type_id': line.product_id.id,
                    'sale_line_id': line.id
                }))
        self.cro_ids = values

    #################################################
    # Report Function
    def generate_draft_bl(self):
        # Find The BL Template
        if self.principal_id:
            url = "/report/pdf/%s/%s" % (self.principal_id.draft_bl_report_id.report_name, self.id)
        else:
            url = ""
        return url

    def action_send_booking(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template = self.env.ref('forecastle_module.email_template_send_booking')
        lang = self.env.context.get('lang')
        # template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template.id),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'mark_so_as_booking': True,
            'model_description': self.with_context(lang=lang).type_name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def action_quotation_send(self):
        res = super(SaleOrder, self).action_quotation_send()
        print('======================== masuk lu ')
        ctx = res.get('context')
        template = self.env.ref('forecastle_module.email_template_proforma')
        if ctx.get('proforma'):
            print('=================== MASUK GA')
            ctx.update({'default_template_id': template.id,
                        'default_attachment_ids': False,
                        })
            self.fal_revise_proforma = True
        # is_import = ctx.get('model_description')
        # if is_import == 'Import':
        #     template = self.env.ref('forecastle_module.email_template_send_noa')
        #     ctx.update({'default_template_id': template.id,
        #                 'default_attachment_ids': [(0, 0, {'name': 'Notice OF Arrival', 'datas': template})],
        #                 'send_noa': True,
        #                 'force_email': True,
        #                 })
        return res

    def action_add_proforma_invoice(self):
        template = self.env.ref('forecastle_module.email_template_proforma')
        vals = {
            'model': 'sale.order',
            'res_id': self.ids[0],
            'template_id': template.id,
            'composition_mode': 'comment',
        }

        if self.invoice_ids:
            mail = self.env['mail.compose.message'].create(vals)
            mail.action_send_mail()

            mail.write({
                'model': 'account.move',
                'res_id': self.invoice_ids.ids and self.invoice_ids.ids[0],
            })

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_so_as_sent'):
            # if not self.charge_info_ids:
                # self.create_charge_info()
            if not self.cro_ids:
                self.create_cro_lines()
        if self.env.context.get('mark_so_as_booking'):
            self.filtered(lambda o: not o.booking_email_send).with_context(tracking_disable=True).write({'booking_email_send': True})
        if self.env.context.get('proforma'):
            self.filtered(lambda o: not o.proforma_send).with_context(tracking_disable=True).write({'proforma_send': True})
        return super(SaleOrder, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['fal_sale_source_id'] = self.id
        res["fal_rate_currency"] = self.fal_rate_currency
        res['source_job'] = 'import_income' if self.is_import else 'export_income'
        return res

    ##########################################################

    def compute_import_report(self):
        data = []
        for x in self.import_container_info_ids:
            data.append([x.product_id, x.con_deposit, x.quantity, x.detention_formula_id.slab_value1, x.detention_formula_id.slab_value2, x.detention_formula_id.slab_value3])

        res = {}
        for name, price, qty, formula1, formula2, formula3 in data:
            if name in res:
                res[name]['nama'] = name.name
                res[name]['uom_qty'] += qty
                res[name]['price'] = price
                res[name]['type'] = name.container_type
                res[name]['size'] = name.container_size
                res[name]['formula1'] = formula1
                res[name]['formula2'] = formula2
                res[name]['formula3'] = formula3
            else:
                res[name] = {'nama': name.name, 'uom_qty':
                qty, 'price': price, 'type': name.container_type, 'size': name.container_size,
                'formula1': formula1, 'formula2': formula2, 'formula3': formula3}

        container_data = []
        for record in res:
            container_data.append(res[record])

        return container_data
    ##########################################################


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    initial_price = fields.Float("Initial Price")
    principal_currency_id = fields.Many2one('res.currency', "Principal Currency")
    price_unit_principal_currency = fields.Float("Unit Price($)")
    principal_id = fields.Many2one('res.partner', related="product_id.principal_id")

    total_by_product_set = fields.Float('Total By product set', compute="_get_total_by_product_set")
    fal_convert_currency = fields.Monetary('Convert currency', compute="_get_total_by_product_set_rupiah", store=True)
    fal_ppn_amount = fields.Monetary('PPN_amount', compute="_get_ppn_amount")
    fal_total_incl_ppn = fields.Monetary('Amount_Inc.PPN', compute="_get_total_incl_ppn")
    fal_price_rupiah = fields.Monetary('Unit Price (Rp)', compute='_action_get_list_price')

    # Extra Information field
    charge_info_partner_id = fields.Many2one('res.partner', compute="_get_charge_info_partner_id")

    # _logger.info('******************************************')
    # def _onchange_product_id(self):
    #     # res = super(SaleOrderLine, self)._onchange_product_id()

    #     for x in self:
    #         if x.product_id.import_charge == True:
    #             total_qty = len(x.order_id.import_container_info_ids.filtered(lambda z: x.product_id.container_size == z.product_id.container_size and x.product_id.container_type == z.product_id.container_type))
    #             x.product_uom_qty = total_qty
    #             _logger.info(x.product_uom_qty)

    #     return super(SaleOrderLine, self)._onchange_product_id()
    # _logger.info('******************************************')

    def _get_charge_info_partner_id(self):
        for sol in self:
            sol.charge_info_partner_id = False
            for charge_info in sol.order_id.charge_info_ids:
                for charge_info_sol in charge_info.sale_line_ids:
                    if sol.id == charge_info_sol.id and charge_info.bill_to_id:
                        sol.charge_info_partner_id = charge_info.bill_to_id

    def _action_get_list_price(self):
        for price in self:
            product = price.product_id.filtered(lambda x: x.is_ofr is not True and not x.is_dollar and not x.import_charge and not x.is_container)
            price.fal_price_rupiah = product.list_price

    @api.model_create_multi
    def create(self, vals_list):
        res = super(SaleOrderLine, self).create(vals_list)
        if res.order_id.charge_info_ids and res.order_id.internal_confirm:
            values = []
            sale_line = []
            for x in res.order_id.charge_info_ids:
                for sale_line_info in x.sale_line_ids:
                    sale_line.append(sale_line_info.id)
            for record in res:
                if record.id not in sale_line:
                    values.append((0, 0, {
                        'name': record.name,
                        'bill_to_id': record.order_id.partner_id.id,
                        'fce_payment_term': 'prepaid',
                        'sale_line_ids': [(6, 0, record.ids)],
                    }))
            res.order_id.charge_info_ids = values
        return res

    def _get_display_price(self, product):
        # Make sure to get Date of the start date
        no_variant_attributes_price_extra = [
            ptav.price_extra for ptav in self.product_no_variant_attribute_value_ids.filtered(
                lambda ptav:
                    ptav.price_extra and
                    ptav not in product.product_template_attribute_value_ids
            )
        ]
        if no_variant_attributes_price_extra:
            product = product.with_context(
                no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
            )

        if self.order_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(date=self.order_id.start_date, pricelist=self.order_id.pricelist_id.id, uom=self.product_uom.id, product_set=self.product_set_id, set=self.product_set_id).price
        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=self.product_uom.id, product_set=self.product_set_id, set=self.product_set_id)

        final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(product or self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, self.order_id.pricelist_id.id)
        if currency != self.order_id.pricelist_id.currency_id:
            base_price = currency._convert(
                base_price, self.order_id.pricelist_id.currency_id,
                self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)

    def _get_ppn_amount(self):
        for sale_line in self:
            sale_line.fal_ppn_amount = 0.1 * sale_line.price_unit

    def _get_total_incl_ppn(self):
        for sale_line in self:
            sale_line.fal_total_incl_ppn = sale_line.price_unit + sale_line.fal_ppn_amount

    @api.depends('total_by_product_set')
    def _get_total_by_product_set_rupiah(self):
        for line in self:
            usd = self.env.ref('base.USD')
            if line.total_by_product_set:
                line.fal_convert_currency = usd._convert(line.total_by_product_set, line.order_id.currency_id, line.order_id.company_id, line.order_id.date_order)
            else:
                line.fal_convert_currency = False

    def _get_total_by_product_set(self):
        for sale_line in self:
            total_by_product_set = 0
            total_by_product_set_usd = 0
            for line in sale_line.order_id.order_line.filtered(lambda a: a.product_set_id == sale_line.product_set_id and not a.do_not_merge):
                total_by_product_set += line.price_unit
                total_by_product_set_usd += line.price_unit_principal_currency
            if sale_line.do_not_merge:
                sale_line.total_by_product_set = total_by_product_set
            else:
                sale_line.total_by_product_set = total_by_product_set_usd

    # If Principal currecy price is changed, Calculate the unit price
    @api.onchange('principal_currency_id', 'price_unit_principal_currency')
    def price_unit_principal_currency_currency_change(self):
        if self.price_unit_principal_currency:
            product = self.product_id
            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self.principal_currency_id._convert(self.price_unit_principal_currency, self.order_id.currency_id, self.order_id.company_id, self.order_id.date_order), product.taxes_id, self.tax_id, self.company_id)

    # When Product Changed
    # Call Method to get MRG USD Price
    @api.onchange('product_id')
    def product_id_change(self):
        vals = {'price_unit_principal_currency': 0, 'principal_currency_id': self.order_id.currency_id.id}
        product_uom_qty = False
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            product_uom_qty = self.product_uom_qty or 1.0
        product = self.product_id.with_context(
            lang=get_lang(self.env, self.order_id.partner_id.lang).code,
            partner=self.order_id.partner_id,
            quantity=product_uom_qty or self.product_uom_qty,
            date=self.order_id.start_date_sales,
            uom=self.product_uom.id,
            product_set=self.product_set_id or self.env.context.get('wizard_set', False)
        )
        # Write Currency in Pricelist Line
        # Get the rule to be used
        if product or self.product_id:
            if self.order_id.pricelist_id:
                final_price, rule_id = self.order_id.pricelist_id.get_product_price_rule(product or self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id, self.order_id.start_date_sales or False)
                # Get the rule on parent pricelist
                if rule_id:
                    rule = self.env['product.pricelist.item'].browse(rule_id)
                    if rule.base_pricelist_id:
                        # Get the rule on parent pricelist
                        base_final_price, base_rule_id = rule.base_pricelist_id.get_product_price_rule(product or self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
                        if base_rule_id:
                            base_rule = self.env['product.pricelist.item'].browse(base_rule_id)
                            # Fix Tax Included for MRG USD Fixed Price
                            vals['price_unit_principal_currency'] = base_rule.fixed_price or 0
                            vals['principal_currency_id'] = base_rule.base_pricelist_id and base_rule.base_pricelist_id.currency_id.id or base_rule.currency_id.id
                        else:
                            vals['price_unit_principal_currency'] = rule.fixed_price or 0
                            vals['principal_currency_id'] = rule.base_pricelist_id and rule.base_pricelist_id.currency_id.id or rule.currency_id.id
                    else:
                        vals['price_unit_principal_currency'] = rule.fixed_price or 0
                        vals['principal_currency_id'] = rule.base_pricelist_id and rule.base_pricelist_id.currency_id.id or rule.currency_id.id

        for x in self:
            if x.product_id.import_charge and x.order_id.is_import:
                total_qty = len(x.order_id.import_container_info_ids.filtered(lambda a: a.product_id.container_size == x.product_id.container_size and a.product_id.container_type == x.product_id.container_type))
                x.product_uom_qty = total_qty
        result = super(SaleOrderLine, self).product_id_change()
        vals['initial_price'] = self.price_unit
        self.update(vals)
        return result

    # Whe Product UoM Chaged, call again method to check price
    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position'),
                product_set=self.product_set_id or self.env.context.get('wizard_set', False)
            )
            self.price_unit = product._get_tax_included_unit_price(
                self.company_id,
                self.order_id.currency_id,
                self.order_id.date_order,
                'sale',
                fiscal_position=self.order_id.fiscal_position_id,
                product_price_unit=self._get_display_price(product),
                product_currency=self.order_id.currency_id
            )
        self.initial_price = self.price_unit
        if not self.product_uom or not self.product_id:
            self.price_unit_principal_currency = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position'),
                product_set=self.product_set_id or self.env.context.get('wizard_set', False)
            )
            # Write Currency in Pricelist Line
            # Get the rule to be used
            final_price, rule_id = self.order_id.pricelist_id.get_product_price_rule(product or self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
            # Get the rule on parent pricelist
            if rule_id:
                rule = self.env['product.pricelist.item'].browse(rule_id)
                if rule.base_pricelist_id:
                    # Get the rule on parent pricelist
                    base_final_price, base_rule_id = rule.base_pricelist_id.get_product_price_rule(product or self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
                    if base_rule_id:
                        base_rule = self.env['product.pricelist.item'].browse(base_rule_id)
                        # Fix Tax Included for MRG USD Fixed Price
                        self.price_unit_principal_currency = self.env['account.tax']._fix_tax_included_price_company(base_rule.fixed_price or 0, product.taxes_id, self.tax_id, self.company_id)
                        self.principal_currency_id = base_rule.currency_id.id
                    else:
                        self.price_unit_principal_currency = self.env['account.tax']._fix_tax_included_price_company(rule.fixed_price or 0, product.taxes_id, self.tax_id, self.company_id)
                        self.principal_currency_id = rule.currency_id.id
                else:
                    self.price_unit_principal_currency = self.env['account.tax']._fix_tax_included_price_company(rule.fixed_price or 0, product.taxes_id, self.tax_id, self.company_id)
                    self.principal_currency_id = rule.currency_id.id

    def _purchase_service_create(self, quantity=False):
        filter_line = False
        if self.order_id.is_import:
            filter_line = self.filtered(lambda x: x.product_id.is_ofr is not True)
        else:
            filter_line = self.filtered(lambda x: x.product_id.is_ofr is True)
        """ On Sales Order confirmation, some lines (services ones) can create a purchase order line and maybe a purchase order.
            If a line should create a RFQ, it will check for existing PO. If no one is find, the SO line will create one, then adds
            a new PO line. The created purchase order line will be linked to the SO line.
            :param quantity: the quantity to force on the PO line, expressed in SO line UoM
        """
        PurchaseOrder = self.env['purchase.order']
        supplier_po_map = {}
        sale_line_purchase_map = {}
        for line in filter_line:
            line = line.with_company(line.company_id)
            # determine vendor of the order (take the first matching company and product)
            suppliers = line.product_id._select_seller(quantity=line.product_uom_qty, uom_id=line.product_uom)
            if not suppliers:
                raise UserError(_("There is no vendor associated to the product %s. Please define a vendor for this product.") % (line.product_id.display_name,))
            supplierinfo = suppliers[0]
            partner_supplier = supplierinfo.name  # yes, this field is not explicit .... it is a res.partner !

            # determine (or create) PO
            # Modify to alwasy create PO or At least PO with the same origin
            purchase_order = supplier_po_map.get(partner_supplier.id)
            if not purchase_order:
                purchase_order = PurchaseOrder.search([
                    ('partner_id', '=', partner_supplier.id),
                    ('state', '=', 'draft'),
                    ('company_id', '=', line.company_id.id),
                    ('origin', '=', line.order_id.name)
                ], limit=1)
            if not purchase_order:
                values = line._purchase_service_prepare_order_values(supplierinfo)
                purchase_order = PurchaseOrder.create(values)
            else:  # update origin of existing PO
                so_name = line.order_id.name
                origins = []
                if purchase_order.origin:
                    origins = purchase_order.origin.split(', ') + origins
                if so_name not in origins:
                    origins += [so_name]
                    purchase_order.write({
                        'origin': ', '.join(origins)
                    })
            supplier_po_map[partner_supplier.id] = purchase_order

            # add a PO line to the PO
            values = line._purchase_service_prepare_line_values(purchase_order, quantity=quantity)
            purchase_line = line.env['purchase.order.line'].create(values)

            # link the generated purchase to the SO line
            sale_line_purchase_map.setdefault(line, line.env['purchase.order.line'])
            sale_line_purchase_map[line] |= purchase_line
        return sale_line_purchase_map

    def _purchase_service_prepare_line_values(self, purchase_order, quantity=False):
        """ Returns the values to create the purchase order line from the current SO line.
            :param purchase_order: record of purchase.order
            :rtype: dict
            :param quantity: the quantity to force on the PO line, expressed in SO line UoM
        """
        self.ensure_one()
        # compute quantity from SO line UoM
        product_quantity = self.product_uom_qty
        if quantity:
            product_quantity = quantity

        purchase_qty_uom = self.product_uom._compute_quantity(product_quantity, self.product_id.uom_po_id)

        # determine vendor (real supplier, sharing the same partner as the one from the PO, but with more accurate informations like validity, quantity, ...)
        # Note: one partner can have multiple supplier info for the same product
        supplierinfo = self.product_id._select_seller(
            partner_id=purchase_order.partner_id,
            quantity=purchase_qty_uom,
            date=purchase_order.date_order and purchase_order.date_order.date(), # and purchase_order.date_order[:10],
            uom_id=self.product_id.uom_po_id
        )
        fpos = purchase_order.fiscal_position_id
        taxes = fpos.map_tax(self.product_id.supplier_taxes_id)
        if taxes:
            taxes = taxes.filtered(lambda t: t.company_id.id == self.company_id.id)

        # compute unit price
        price_unit = 0.0
        if supplierinfo:
            # Here we adjust the price, if Sales % is available, it means, we should take sales price and get % amount of it
            if supplierinfo.percentage:
                price_unit = self.env['account.tax'].sudo()._fix_tax_included_price_company(self.price_unit * supplierinfo.percentage / 100, self.product_id.supplier_taxes_id, taxes, self.company_id)
            else:
                price_unit = self.env['account.tax'].sudo()._fix_tax_included_price_company(supplierinfo.price, self.product_id.supplier_taxes_id, taxes, self.company_id)
            if purchase_order.currency_id and supplierinfo.currency_id != purchase_order.currency_id:
                price_unit = supplierinfo.currency_id.compute(price_unit, purchase_order.currency_id)

        return {
            'name': '[%s] %s' % (self.product_id.default_code, self.name) if self.product_id.default_code else self.name,
            'product_qty': purchase_qty_uom,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_po_id.id,
            'price_unit': price_unit,
            'date_planned': fields.Date.from_string(purchase_order.date_order) + relativedelta(days=int(supplierinfo.delay)),
            'taxes_id': [(6, 0, taxes.ids)],
            'order_id': purchase_order.id,
            'sale_line_id': self.id,
        }

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        res['fal_sale_price'] = self.price_unit_principal_currency
        res['fal_principal_currency_id'] = self.principal_currency_id

        return res

    def _check_line_unlink(self):
        """
        Check wether a line can be deleted or not.

        Lines cannot be deleted if the order is confirmed; downpayment
        lines who have not yet been invoiced bypass that exception.
        :rtype: recordset sale.order.line
        :returns: set of lines that cannot be deleted
        """
        return self.filtered(lambda line: line.state in ('done') and (line.invoice_lines or not line.is_downpayment))


class ChargeInfo(models.Model):
    _name = 'charge.info'

    # Invoicing
    name = fields.Char(string="Charge Item")
    fce_payment_term = fields.Selection([
        ('prepaid', 'Prepaid'),
        ('collect', 'Collect'),
    ], string="Payment Term")
    bill_to_id = fields.Many2one('res.partner', string="Bill To")
    sale_id = fields.Many2one('sale.order', string="Sale")
    sale_line_ids = fields.Many2many('sale.order.line', string="Sale Line")
