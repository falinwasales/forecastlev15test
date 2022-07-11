# -*- coding: utf-8 -*-
from odoo import fields, models, api
import datetime
import odoo.addons.decimal_precision as dp


class account_invoice(models.Model):
    _inherit = 'account.move'

    def _get_effective_payment_dates(self):
        for invoice in self:
            payment_obj = self.env['account.payment']
            temp = []
            payment_ids = payment_obj.search([('partner_id', '=', invoice.partner_id.id)])
            payments = payment_ids.filtered(lambda a: invoice.id in a.reconciled_invoice_ids.ids)
            for payment in payments:
                temp.append(fields.Date.to_string(payment.date))
            invoice.fal_effective_payment_dates = ";".join(temp)

    @api.depends('partner_id')
    def _get_parent_company(self):
        for move in self:
            move.fal_parent_company = move.partner_id.parent_id or False

    commercial_partner_id = fields.Many2one('res.partner', string='Commercial Entity', compute_sudo=True,
        related='partner_id.commercial_partner_id', store=True, readonly=True,
        help="The commercial entity that will be used on Journal Entries for this invoice")

    fal_parent_company = fields.Many2one(
        'res.partner',
        compute='_get_parent_company',
        string='Parent Company',
        help='The Parent Company for group',
        readonly=True,
        store=True
    )

    final_quotation_number = fields.Char(string='Final Quotation', size=64)
    fal_attachment = fields.Binary(string='Invoice Attachment', attachment=True)
    fal_attachment_name = fields.Char(string='Attachment name')
    fal_client_order_ref = fields.Char(
        'Customer PO Number', size=64, index=True)

    fal_supplier_order_ref = fields.Char(
        'Supplier PO Number', size=64, index=True)

    fal_quotation_number = fields.Char(
        'Quotation Number', size=64,
        readonly=True, index=True
    )
    fal_risk_level = fields.Integer(
        string='Risk Level',
        help="Risk Level define in number 1 - 9"
    )
    fal_risk_level_name = fields.Char(
        'Risk Level Name',
        size=64,
        help="Risk Level Name"
    )
    fal_effective_payment_dates = fields.Char(
        compute='_get_effective_payment_dates',
        string='Effective Payment Dates',
        help="The efective payment dates.",
    )
    fal_use_late_payment_statement = fields.Boolean(
        'Use Late Payment Statement', default=lambda self:
        self.env['res.users'].browse(self._uid).company_id.fal_company_late_payment_statement, help="Use Late Payment Statement"
    )
    fal_company_code = fields.Char(
        related='company_id.company_registry',
        string='Company Code'
    )

    def _get_total_ordered_amount(self):
        for invoice in self:
            total = 0
            invoice.fal_total_ordered_amount = total

    def _get_total_invoiced_amount(self):
        for invoice in self:
            total = 0
            invoice_list = []
            for item in invoice_list:
                total += item.amount_untaxed if item.move_type in ['out_invoice', 'in_invoice'] else -item.amount_untaxed
            invoice.fal_total_amount_already_invoced = total

    def _get_percentage_invoiced_ordered(self):
        for invoice in self:
            amount_percentage = 0.0
            if invoice.fal_total_ordered_amount:
                amount_percentage = invoice.fal_total_amount_already_invoced / invoice.fal_total_ordered_amount * 100
            invoice.fal_percentage_invoiced_ordered = amount_percentage

    # fal_total_ordered_amount = fields.Monetary(
    #     string='Total ordered amount', compute="_get_total_ordered_amount")
    # fal_total_amount_already_invoced = fields.Monetary(
    #     string='Total invoiced amount', compute="_get_total_invoiced_amount")
    # fal_percentage_invoiced_ordered = fields.Float(
    #     string='% Invoiced / ordered', compute='_get_percentage_invoiced_ordered')

    #################################################################################
    # If there is attachment, we register it
    def write(self, vals):
        res = super(account_invoice, self).write(vals)
        for move in self:
            if move.fal_attachment:
                new_attachment = self.env['ir.attachment'].with_context(no_document=False).create({
                    'name': move.fal_attachment_name,
                    'type': 'binary',
                    'datas': move.fal_attachment,
                })
                # To avoid double attachment, check the checksum
                duplicate = self.env['ir.attachment'].search([('res_model', '=', 'account.move'), ('res_id', '=', move.id), ('checksum', '=', new_attachment.checksum)])
                if not duplicate:
                    new_attachment.write(
                        {'res_model': 'account.move',
                         'res_id': move.id})
        return res

    @api.model_create_multi
    def create(self, vals_list):
        moves = super(account_invoice, self).create(vals_list)
        for move in moves:
            if move.fal_attachment:
                new_attachment = self.env['ir.attachment'].with_context(no_document=False).create({
                    'name': move.fal_attachment_name,
                    'type': 'binary',
                    'datas': move.fal_attachment,
                })
                # To avoid double attachment, check the checksum
                duplicate = self.env['ir.attachment'].search([('res_model', '=', 'account.move'), ('res_id', '=', move.id), ('checksum', '=', new_attachment.checksum)])
                if not duplicate:
                    new_attachment.write(
                        {'res_model': 'account.move',
                         'res_id': move.id})
        return moves
