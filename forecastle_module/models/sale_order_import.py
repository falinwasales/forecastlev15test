# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta
from odoo.tools import float_compare
from odoo.exceptions import UserError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_import = fields.Boolean('Import')

    almt_consignee = fields.Char('ALMT Consignee')
    npwp_consignee = fields.Char('NPWP Consignee')
    nama_shipper = fields.Char('Nama Shipper')
    almt_shipper = fields.Char('ALMT Shipper')
    nama_notify = fields.Char('Nama Notify')
    almt_notify = fields.Char('ALMT Notify')
    no_voyage = fields.Char('NO Voyage / Arrival')
    mother_vessel = fields.Char('Mother Vessel')
    nama_sarana_angkut = fields.Char('Name Sarana Angkut')
    tgl_tiba = fields.Date('TGL Tiba')
    jam_tiba = fields.Char('Jam Tiba')
    no_master_bl = fields.Char('NO Master BL/AWB')
    tgl_master_bl = fields.Char('TGL Master BL/AWB')
    no_host_bl = fields.Char('No AJU')
    tgl_host_bl = fields.Char('TGL Host BL/AWB')
    no_pos = fields.Char('NO POS')
    no_sub_pos = fields.Char('NO Sub POS')
    no_sub_sub_pos = fields.Char('NO Sub Sub POS')
    pelabuhan_asal = fields.Many2one('fce.port.code', 'Pelabuhan Asal')
    pelabuhan_transit = fields.Many2one('fce.port.code', 'Pelabuhan Transit')
    pelabuhan_bongkar = fields.Many2one('fce.port.code', 'Pelabuhan Bongkar')
    pelabuhan_akhir = fields.Many2one('fce.port.code', 'Pelabuhan akhir')
    jumlah_kemasan = fields.Char('Jumlah Kemasan')
    jenis_kemasan = fields.Char('Jenis Kemasan')
    bruto = fields.Char('Bruto')
    volume = fields.Char('Volume')
    hs_code = fields.Char('HS Code')
    uraian_barang = fields.Char('Uraian Barang')
    noa = fields.Boolean('Noa', copy=False)
    noa_confirmed = fields.Boolean('Noa Confirmed', copy=False)
    repair = fields.Boolean('repair', compute='_check_repair')
    release_spdo = fields.Boolean('Release SPDO')

    # Container Info
    import_container_info_ids = fields.One2many('import.container.info', 'sale_id', string="Container Info")

    # Document Info
    imp_principal_id = fields.Many2one('res.partner', string="Principal Import", domain="[('is_principal', '=', True)]")
    imp_terminal_code_id = fields.Many2one('fce.terminal.code', string="Terminal Code")
    imp_depot_code_id = fields.Many2one('fce.port.code', string="Depot Code")
    attn = fields.Char('Attn')
    ata_jkt = fields.Date('ATA JKT')
    batas_pengembalian = fields.Date('Container Return Date', related='import_container_info_ids.last_date')
    hbl = fields.Binary('HBL')
    filename_hbl = fields.Char('Filename HBL')
    import_manifest = fields.Binary('Inward Manifest')
    filename_import_manifest = fields.Char('Filename Inward Manifest')

    deposit_ids = fields.Many2many('account.move', string="Deposit Entries", compute='_get_deposit_entries')
    deposit_count = fields.Integer(compute='_get_deposit_entries', store=False)
    purchase_delivery_count = fields.Integer(compute='_get_delivery_count')
    commission_invoice_id = fields.Many2one('account.move', string="Commission Invoice", copy=False)
    deposit_invoice_id = fields.Many2one('account.move', string="Deposit Container", copy=False)
    detention_invoice_id = fields.Many2one('account.move', string="Detention Invoice (Actual)", copy=False)
    deposit_detention_invoice_id = fields.Many2one('account.move', string="Deposit Detention (Internal)", copy=False)

    # Repair
    fce_repair_id = fields.Many2one('fce.repair', string="Repair", copy=False)

    po_detention_id = fields.Many2one('purchase.order', string="Purchase Order Detention", copy=False)
    po_comision_ehs = fields.Many2one('purchase.order', string="Purchase Order EHS", copy=False)
    po_repair_ids = fields.One2many('purchase.order', 'so_repair_id', string="Purchase Order Repair Principal")
    po_repair_consignee_ids = fields.One2many('purchase.order', 'so_repair_consignee_id', string="Purchase Order Repair Principal")
    so_vendor_bill_ids = fields.One2many('account.move', 'so_vendor_bill_id', string="So Vendor Bill")
    po_repair_count = fields.Integer(compute='_compute_purchase_order_repair_count', string='Purchase Order Repair Count')
    po_repair_consignee_count = fields.Integer(compute='_compute_purchase_order_repair_count', string='Purchase Order Repair Consignee Count')
    so_vendor_bill_count = fields.Integer(compute='_compute_so_vendor_bill_count', string='Purchase Order Repair Count')
    c2c_purchase_count = fields.Integer(compute='_compute_c2c_purchase_count', string='Purchase Order C2C Count')

    #  Refund Deposit
    ktp = fields.Binary('KTP')
    ktp_date_submit = fields.Date(string='KTP Date Submited')
    filename_ktp = fields.Char('Filename KTP')
    surat_kuasa = fields.Binary('Surat Kuasa')
    surat_kuasa_date_submit = fields.Date(string='Surat Kuasa Date Submited')
    filename_surat_kuasa = fields.Char('Filename Surat Kuasa')
    bl = fields.Binary('BL')
    bl_date_submit = fields.Date(string='BL Date Submited')
    filename_bl = fields.Char('Filename BL')
    eir = fields.Binary('EIR')
    eir_date_submit = fields.Date(string='EIR Date Submited')
    filename_eir = fields.Char('Filename EIR')
    sp2 = fields.Binary('SP2')
    sp2_date_submit = fields.Date(string='SP2 Date Submited')
    filename_sp2 = fields.Char('Filename SP2')
    bukti_bayar = fields.Binary('Bukti Bayar')
    bukti_bayar_date_submit = fields.Date(string='Bukti Bayar Date Submited')
    filename_bukti_bayar = fields.Char('Filename Bukti Bayar')
    official_receipt = fields.Binary('Official Receipt')
    official_receipt_date_submit = fields.Date(string='Official Receipt Date Submited')
    filename_official_receipt = fields.Char('Filename Official Receipt')
    invoice_detention = fields.Binary('Invoice Detention')
    invoice_detention_date_submit = fields.Date(string='Invoice Detention Date Submited')
    filename_invoice_detention = fields.Char('Filename Invoice Detention')
    official_receipt_detention = fields.Binary('Official Receipt Detention')
    official_receipt_detention_date_submit = fields.Date(string='Official Receipt Date Submited')
    refund_invocie_detention = fields.Boolean(string='Refund Invoice Detention')
    filename_official_receipt_detention = fields.Char('Filename Official Receipt Detention')
    refund_official_receipt_detention = fields.Boolean(string='Refund Official Receipt Detention')
    discharge_date = fields.Date(string="Discharge Date", related='import_container_info_ids.date_of_arrival')
    gate_out_cy_date = fields.Date(string="Gate Out CY")

    #  voyage_id
    voyage_id = fields.Many2one('fce.voyage', string="NO Voyage / Arrival", copy=False)

    def _get_group_container(self):
        data_cont = []
        for x in self.import_container_info_ids:
            data_cont.append([x.product_id.id, x.quantity, x])

        res_cont = {}
        for product, qty, line_id in data_cont:
            if product in res_cont:
                res_cont[product]['product_id'] = product
                res_cont[product]['qty'] += qty
                res_cont[product]['container_info_ids'] += line_id
            else:
                res_cont[product] = {'product_id': product, 'qty': qty, 'container_info_ids': line_id}

        container_data_cont = []
        for record in res_cont:
            containers = res_cont[record].get('container_info_ids')
            res_cont[record].update({'container_info_ids': [(6, 0, containers.ids)]})
            container_data_cont.append(res_cont[record])

        return container_data_cont

    def _report_noa(self):
        data_cont = []
        for x in self.import_container_info_ids:
            data_cont.append([x.product_id.id, x.product_id, x.quantity])

        res_cont = {}
        for product, product_id, quantity in data_cont:
            if product in res_cont:
                res_cont[product]['product_id'] = product_id.name
                res_cont[product]['size'] = product_id.container_size
                res_cont[product]['type'] = product_id.container_type
                res_cont[product]['qty'] += quantity
            else:
                res_cont[product] = {'product_id': product_id.name, 'size': product_id.container_size, 'type': product_id.container_type, 'qty': quantity}

        container_product = []
        for record in res_cont:
            container_product.append(res_cont[record])

        return container_product

    # @api.onchange('discharge_date')
    # def _onchange_discharge_date(self):
    #     self.import_container_info_ids.date_of_arrival = self.discharge_date

    def action_release_spdo(self):
        for x in self:
            x.release_spdo = True

    def _auto_create_invoice_import(self):
        for sale in self:
            group_by_partner = []
            for charge in sale.charge_info_ids:
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
            # for line in sale.order_line.filtered(lambda a: a.product_id.is_container):
            #     line.write({'qty_delivered': 0})

            for partner in res:
                for charge_info in res[partner]:
                    for line in charge_info.sale_line_ids.filtered(lambda a: a.product_id):
                        line.write({'qty_delivered': line.product_uom_qty})

                sale._generate_wizard_invoice()

                for charge_info in res[partner]:
                    # Write Bill to, to invoice
                    for line in charge_info.sale_line_ids.filtered(lambda a: a.product_id and a.display_type not in ['line_section']):
                        inv_line = line.invoice_lines
                        inv_line.move_id.write({'partner_id': partner.id})
        # for sale in self:
        #     # For Type import
        #     if sale.is_import:
        #         for line in sale.order_line.filtered(lambda x: x.product_uom_qty != 0.0):
        #             line.write({'qty_delivered': line.product_uom_qty})
        #         sale._generate_wizard_invoice()

    def update_detention_info(self):
        for sale in self:
            for container in sale.import_container_info_ids:
                container._onchange_container_size_type()

    def _compute_so_vendor_bill_count(self):
        self.so_vendor_bill_count = len(self.so_vendor_bill_ids)

    def _compute_c2c_purchase_count(self):
        count = self.env['purchase.order'].search([('sales_source_id_is_import', '=', self.name), ('is_receipt', '=', False)])
        self.c2c_purchase_count = len(count)

    def _compute_purchase_order_repair_count(self):
        self.po_repair_count = len(self.po_repair_ids)
        self.po_repair_consignee_count = len(self.po_repair_consignee_ids)

    def action_repair(self):
        for sale in self:
            picking_ids = sale._get_delivery_purchase()
            if picking_ids:
                repair_id = sale.fce_repair_id
                if not repair_id:
                    repair_id = self.env['fce.repair'].create({})
                    sale.fce_repair_id = repair_id.id
                pickings = self.env['stock.picking'].browse(picking_ids)
                for picking in picking_ids:
                    if all(not move.actual_gate for move in pickings.move_line_ids_without_package):
                        raise UserError(_('No repaired by set on receipt order'))

                    for line in pickings.move_line_ids_without_package:
                        line.write({
                            'fce_repair_id': repair_id.id,
                            'consignee_id': sale.partner_id.id if line.repaired_by == 'consignee' else False,
                            'principal_id': sale.imp_principal_id.id if line.repaired_by == 'principal' else False,
                        })

    def _check_repair(self):
        for sale in self:
            repair = False
            picking_ids = sale._get_delivery_purchase()
            if picking_ids:
                pickings = self.env['stock.picking'].browse(picking_ids)
                for picking in picking_ids:
                    if any(move.repair_status for move in pickings.move_line_ids_without_package):
                        repair = True
            sale.repair = repair

    @api.depends('state')
    def _compute_type_name(self):
        for record in self:
            if record.is_import:
                record.type_name = "Import"
            else:
                return super(SaleOrder, self)._compute_type_name()

    def _get_delivery_count(self):
        for sale in self:
            picking_ids = sale._get_delivery_purchase()
            sale.purchase_delivery_count = len(picking_ids)

    def _get_deposit_entries(self):
        for sale in self:
            deposit_ids = []
            for con in sale.import_container_info_ids:
                lines = self.env['account.move.line'].search([('import_container_id', '=', con.id)])
                for line in lines:
                    if line.move_id and line.move_id.id not in deposit_ids:
                        deposit_ids.append(line.move_id.id)
            sale.deposit_ids = [(6, 0, deposit_ids)]
            sale.deposit_count = len(deposit_ids)

    def so_revision_quote(self):
        action = super(SaleOrder, self).so_revision_quote()
        res_id = action['res_id']
        if self.is_import:
            action = self.env.ref('forecastle_module.sale_order_import_action').read()[0]
            action['views'] = [(self.env.ref('forecastle_module.view_sale_order_import_form').id, 'form')]
            action['res_id'] = res_id
        return action

    # @api.depends('order_line.invoice_lines')
    # def _get_invoiced(self):
    #     # The invoice_ids are obtained thanks to the invoice lines of the SO
    #     # lines, and we also search for possible refunds created directly from
    #     # existing invoices. This is necessary since such a refund is not
    #     # directly linked to the SO.
    #     for order in self:
    #         if order.is_import:
    #             invoices = order.order_line.invoice_lines.move_id.filtered(lambda r: r.move_type in ('out_invoice', 'out_refund'))
    #             invoices |= order.deposit_ids
    #             order.invoice_ids = invoices
    #             order.invoice_count = len(invoices)
    #         else:
    #             super(SaleOrder, order)._get_invoiced()

    def action_view_deposit(self):
        deposit_ids = self.mapped('deposit_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        action['domain'] = [('id', 'in', deposit_ids.ids)]
        action['context'] = False
        return action

    def _get_delivery_purchase(self):
        purchase_order_ids = self._get_purchase_orders()
        picking_ids = []
        for purchase in purchase_order_ids:
            for picking in purchase.picking_ids:
                picking_ids.append(picking.id)
        return picking_ids

    def action_view_purchase_delivery(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        picking_ids = self._get_delivery_purchase()
        action['domain'] = [('id', 'in', picking_ids)]
        return action

    def action_send_noa(self):
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

    def action_set_ofr(self):
        group_container = self._get_group_container()

        lines = []
        for group in group_container:
            lines.append((0, 0, group))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Set OFR'),
            'view_mode': 'form',
            'res_model': 'set.ofr.wizard',
            'target': 'new',
            'context': {'default_ofr_line_ids': lines},
        }

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('send_noa'):
            self.filtered(lambda o: not o.noa).with_context(tracking_disable=True).write({'noa': True})
        return super(SaleOrder, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self._create_container_deposit()
        self._create_invoice_commission_import()
        self._create_deposit_detention_invoice_import()
        self._create_purchase_ehs()
        # self._auto_create_invoice_import()
        if self.is_import:
            values = []
            for line in self.order_line.filtered(lambda a: a.display_type not in ['line_section']):
                values.append((0, 0, {'name': line.name,
                        'bill_to_id': line.order_id.partner_id.id,
                        'fce_payment_term': 'prepaid',
                        'sale_line_ids': [(6, 0, line.ids)]}))
            self.charge_info_ids = values
        return res

    def _create_purchase_ehs(self):
        if self.is_import:
            is_ehs = self.order_line.filtered(lambda a: a.product_id.is_ehs_comision is True)
            if is_ehs:
                po = self.env['purchase.order'].create({
                    'partner_id': self.imp_principal_id.id,
                    'sales_source_id': self.id,
                    'currency_id': self.env.ref('base.USD').id,
                    'order_line': []
                })
                vals = []
                for x in self.order_line.filtered(lambda a: a.product_id.is_ehs_comision is True):
                    vals.append((0, 0, {
                        'name': x.product_id.name,
                        'sale_line_id': x.id,
                        'product_id': x.product_id.id,
                        'product_qty': x.product_uom_qty,
                        'product_uom': x.product_uom.id,
                        'price_unit': x.price_unit_principal_currency,
                        'date_planned': datetime.today(),
                        'taxes_id': x.tax_id,
                    }))
                po.write({'order_line': vals})
                self.po_comision_ehs = po.id

    def _create_container_deposit(self):
        for sale in self:
            if sale.is_import:
                journal_id = self.env['account.journal'].search([('type', 'in', ['sale']), ('operating_unit_id', '=', sale.operating_unit_id.id)], limit=1)
                invoice_vals = {
                    'partner_id': sale.partner_id.id,
                    'fal_sale_source_id': sale.id,
                    'move_type': 'out_invoice',
                    'currency_id': sale.currency_id.id,
                    'invoice_origin': self.name,
                    'company_id': sale.company_id.id,
                    'invoice_user_id': self.user_id and self.user_id.id,
                    'invoice_line_ids': [],
                    'journal_id': journal_id and journal_id.id or False,
                    'fal_invoice_type': 'container',
                }

                for line in sale.import_container_info_ids:
                    account_id = line.product_id.account_container_deposit_id.id or line.product_id.categ_id.account_container_deposit_id.id
                    if not account_id:
                        raise UserError(_('Please set container deposit account on product %s') % (line.product_id.display_name))

                    line_vals = {
                        'product_id': line.product_id.id,
                        'name': line.no_container,
                        'price_unit': line.con_deposit,
                        'account_id': account_id,
                        'import_container_id': line.id,
                        'analytic_account_id': sale.analytic_account_id.id,
                    }
                    invoice_vals['invoice_line_ids'].append((0, 0, line_vals))

                if invoice_vals['invoice_line_ids']:
                    move = self.env['account.move'].create(invoice_vals)
                    sale.deposit_invoice_id = move.id

    def _create_purchase_order(self):
        action = {
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'name': _("Purchase Order Repair"),
            'view_mode': 'form',
            'context': {},
        }
        return action

    def action_create_manual_purchase_order_principal(self):
        self.ensure_one()
        action = self._create_purchase_order()
        action.update({
            'context': {
                'analytic_account_id': self.analytic_account_id.id,
                'default_sales_source_id': self.id,
                'default_so_repair_id': self.id,
                'default_principal_id': self.imp_principal_id.id,
                'default_is_repair': True,
            }
        })
        return action

    def action_create_manual_purchase_order_consignee(self):
        self.ensure_one()
        action = self._create_purchase_order()
        action.update({
            'context': {
                'analytic_account_id': self.analytic_account_id.id,
                'default_sales_source_id': self.id,
                'default_so_repair_consignee_id': self.id,
                'default_is_repair': True,
            }
        })
        return action

    def action_view_purchase_repair_principal(self):
        action = self.action_create_manual_purchase_order_principal()
        action.update({
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.po_repair_ids.ids)]
        })
        return action

    def action_view_purchase_repair_consignee(self):
        action = self.action_create_manual_purchase_order_consignee()
        action.update({
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.po_repair_consignee_ids.ids)]
        })
        return action

    def action_create_vendor_bill_import(self):
        action = {
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'name': _("Vendor Bills"),
            'view_mode': 'form',
            'context': {
                'analytic_account_id': self.analytic_account_id.id,
                'default_fal_sale_source_id': self.id,
                'default_move_type': 'in_invoice',
                'default_so_repair_consignee_id': self.id,
            },
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.so_vendor_bill_ids.ids)]
        }
        return action

    def action_create_purchase_c2c(self):
        action = {
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'name': _("Purchase Order"),
            'view_mode': 'form',
            'context': {
                'default_partner_id': self.voyage_id.slot_owner_ids[0].vendor_ids.id,
                'default_currency_id': self.currency_id.id,
                'default_sales_source_id': self.id,
            },
            'view_mode': 'tree,form',
            'domain': [('sales_source_id_is_import', '=', self.name), ('is_receipt', '=', False)]
        }
        return action

    def _create_deposit_detention_invoice_import(self):
        for sale in self:
            if sale.is_import:
                idr = self.env.ref('base.IDR')
                journal_id = self.env['account.journal'].search([('type', 'in', ['sale']), ('operating_unit_id', '=', sale.operating_unit_id.id)], limit=1)
                invoice_vals = {
                    'partner_id': sale.partner_id.id,
                    'fal_sale_source_id': sale.id,
                    'move_type': 'out_invoice',
                    'invoice_origin': self.name,
                    'company_id': sale.company_id.id,
                    'invoice_user_id': self.user_id and self.user_id.id,
                    'invoice_line_ids': [],
                    'journal_id': journal_id and journal_id.id or False,
                    'fal_invoice_type': 'detention',
                }
                invoice_lines = []

                for detention in sale.import_container_info_ids.filtered(lambda x:x.detention_days > 0):
                    detention_charge = detention.total_detention_deposit
                    if detention.currency_id != idr:
                        detention_charge = detention.currency_id._convert(
                            detention.total_detention_deposit,
                            idr,
                            sale.company_id,
                            fields.Date.today()
                        )

                    product_id = self.env.ref('forecastle_module.deposit_detention_product')
                    account_id = product_id.account_container_deposit_id.id or product_id.categ_id.account_container_deposit_id.id
                    if not account_id:
                        raise UserError(_('Please set container deposit account on product %s') % (product_id.display_name))

                    invoice_lines.append((0, 0, {
                        'product_id': product_id.id,
                        'name': detention.no_container,
                        'price_unit': detention_charge,
                        'account_id': account_id,
                        'analytic_account_id': sale.analytic_account_id.id,
                    }))

                if invoice_lines:
                    invoice_vals['invoice_line_ids'] = invoice_lines
                    move = self.env['account.move'].create(invoice_vals)
                    sale.deposit_detention_invoice_id = move.id

    def _create_invoice_commission_import(self):
        for sale in self:
            if sale.is_import:
                usd = self.env.ref('base.USD')
                commission_product = sale.imp_principal_id.product_commission_id
                if not commission_product:
                    raise UserError(_('Please Set Commission Product on Principal: %s') % (sale.imp_principal_id.name,))

                # Find the correct journal
                journal_id = self.env['account.journal'].search([('type', 'in', ['sale']), ('operating_unit_id', '=', sale.operating_unit_id.id)], limit=1)

                invoice_vals = {
                    'partner_id': sale.imp_principal_id.id,
                    'fal_sale_source_id': sale.id,
                    'source_job': 'import_commission',
                    'move_type': 'out_invoice',
                    'currency_id': usd.id,
                    'fal_invoice_mode': 'commission',
                    'invoice_origin': self.name,
                    'company_id': sale.company_id.id,
                    'invoice_user_id': self.user_id and self.user_id.id,
                    'invoice_line_ids': [],
                    'journal_id': journal_id and journal_id.id or False
                }

                commission = self.env['commission.export'].search([
                    ('principal_id', '=', sale.imp_principal_id.id),
                    ('customer_status', '=', sale.customer_status),
                ], limit=1)

                data_category = []
                res = {}

                for container in sale.import_container_info_ids:
                    data_category.append([container.size, container])

                for key, val in data_category:
                    if key in res:
                        res[key] += [val]
                    else:
                        res[key] = [val]

                for product_category in res:
                    lines = res[product_category]
                    commission_line = commission.commission_line_ids.filtered(lambda a: a.commission_type == 'import' and a.product_category_id.id == product_category.id)
                    total_amount = 0

                    container_no = ''
                    for line in lines:
                        container_no += line.no_container_id.name or '' + ', '
                        total_amount += line.ofr

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

                        description = product_category.display_name + ': ' + container_no

                        line_vals = {
                            'product_id': commission_product.id,
                            'name': description  or '',
                            'tax_ids': commission_line.tax_ids,
                            'price_unit': commission_amount,
                            'quantity': len(self.import_container_info_ids),
                            'import_container_id': container.id,
                            'analytic_account_id': sale.analytic_account_id.id,
                        }
                        invoice_vals['invoice_line_ids'].append((0, 0, line_vals))

                if invoice_vals['invoice_line_ids']:
                    move = self.env['account.move'].create(invoice_vals)
                    sale.commission_invoice_id = move.id


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _purchase_service_prepare_line_values(self, purchase_order, quantity=False):
        res = super(SaleOrderLine, self)._purchase_service_prepare_line_values(purchase_order, quantity)
        res['price_unit'] = self.price_unit_principal_currency
        res['account_analytic_id'] = self.order_id.analytic_account_id.id
        return res

    # Generate PO and add container
    def _purchase_service_generation(self):
        result = super(SaleOrderLine, self)._purchase_service_generation()
        purchase_id = False
        if result:
            for value in result:
                res = result.get(value)
                purchase_id = res.order_id

        if purchase_id:

            if self.order_id.is_import:
                usd = self.env.ref('base.USD')
                idr = self.env.ref('base.IDR')
                purchase_id.write({
                    'partner_id': self.order_id.partner_id,
                    'sales_source_id': self.order_id.id,
                    'currency_id': usd.id,
                    'is_receipt': True,
                })
                for con in self.order_id.import_container_info_ids:
                    price_unit = idr._convert(
                        con.con_deposit,
                        usd,
                        con.sale_id.company_id,
                        con.sale_id.date_order or fields.Date.today()
                    )

                    vals = {
                        'name': con.no_container_id.name or con.no_container,
                        'account_analytic_id': con.sale_id.analytic_account_id.id,
                        'product_qty': con.quantity,
                        'product_id': con.product_id.id,
                        'product_uom': con.product_id.uom_po_id.id,
                        'price_unit': 0.0,
                        'import_container_info_id': con.id,
                        'date_planned': fields.Date.today(),
                        'order_id': purchase_id.id,
                    }
                    self.env['purchase.order.line'].create(vals)
                purchase_id.button_confirm()
            else:
                purchase_id.write({
                    'partner_id': self.order_id.principal_id,
                    'sales_source_id': self.order_id.id,
                    'currency_id': self.env.ref('base.USD').id,
                })
                # for line in self.order_id.order_line.filtered(lambda a: a.product_id.is_container):
                #     vals = {
                #         'name': line.product_id.display_name,
                #         'product_qty': line.product_uom_qty,
                #         'product_id': line.product_id.id,
                #         'product_uom': line.product_uom.id,
                #         'price_unit': line.price_unit,
                #         'date_planned': fields.Date.today(),
                #         'order_id': purchase_id.id,
                #     }
                #     self.env['purchase.order.line'].create(vals)

        return result
