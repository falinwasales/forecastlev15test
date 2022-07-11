# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fal_attachment = fields.Binary(string='Reference Attachment')
    fal_attachment_name = fields.Char(string='Attachment name')

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.company_id.fal_company_late_payment_statement:
            res['fal_use_late_payment_statement'] = True
        if self.client_order_ref:
            res['fal_client_order_ref'] = self.client_order_ref
        return res

    # sale archive
    active = fields.Boolean(
        'Active', default=True,
        help="If unchecked, it will allow you to hide\
        the Sale Order without removing it.")

    @api.depends('partner_id')
    def _get_parent_company(self):
        for sale_order in self:
            sale_order.fal_parent_company = sale_order.partner_id.parent_id or False


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

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        for order in self:
            if order.fal_attachment:
                so_attachment = self.env['ir.attachment'].with_context(no_document=False).create({
                    'name': order.fal_attachment_name,
                    'type': 'binary',
                    'datas': order.fal_attachment,
                })
                # To avoid double attachment, check the checksum
                duplicate = self.env['ir.attachment'].search([('res_model', '=', 'sale.order'), ('res_id', '=', order.id), ('checksum', '=', so_attachment.checksum)])
                if not duplicate:
                    so_attachment.write(
                        {'res_model': 'sale.order',
                         'res_id': order.id})
        return res

    @api.model_create_multi
    def create(self, vals):
        result = super(SaleOrder, self).create(vals)
        if result.fal_attachment:
            so_attachment = self.env['ir.attachment'].with_context(no_document=False).create({
                'name': result.fal_attachment_name,
                'type': 'binary',
                'datas': result.fal_attachment,
            })
            so_duplicate = self.env['ir.attachment'].search([('res_model', '=', 'sale.order'), ('res_id', '=', result.id), ('checksum', '=', so_attachment.checksum)])
            _logger.info(so_duplicate, "this so_duplicate")
            if not so_duplicate:
                so_attachment.write(
                    {'res_model': 'sale.order',
                     'res_id': result.id})

        return result
