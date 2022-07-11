# Copyright 2019 VentorTech OU
# License OPL-1.0 or later.

from odoo import models, fields, _
from odoo.exceptions import UserError


class ShippingLabel(models.Model):
    """ Shipping Label entity from Delivery Carrier
    """
    _name = 'shipping.label'
    _description = 'Shipping Label'
    _rec_name = 'picking_id'
    _order = 'create_date desc'

    carrier_id = fields.Many2one(
        comodel_name='delivery.carrier',
        string='Delivery Carrier',
        required=True,
        readonly=True,
    )

    picking_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Delivery Order',
        domain='[("picking_type_id.code", "=", "outgoing")]',
        required=True,
        readonly=True,
    )

    tracking_numbers = fields.Char(
        string='Tracking Number(s)',
        readonly=True,
    )

    label_ids = fields.One2many(
        comodel_name='shipping.label.document',
        inverse_name='shipping_id',
        string='Shipping Label(s)',
        readonly=True,
        copy=False,
    )

    label_status = fields.Selection(
        [
            ('active', 'Active'),
            ('inactive', 'In Active'),
        ],
        string='Status',
    )

    def _get_attachment_list(self):
        self.ensure_one()
        attachment_list = []
        paper_id = self.carrier_id.autoprint_paperformat_id

        def update_attachment_list(label):
            doc = label.document_id
            params = {
                'title': doc.name,
                'type': 'qweb-pdf' if doc.mimetype == 'application/pdf' else 'qweb-text',
                'size': paper_id,
            }
            if label.package_id:
                params['package_id'] = label.package_id
            attachment_list.append((doc.datas.decode('ascii'), params))

        # If there is a label in the context, then the print was called through the print button
        # of one specific label
        if self._context.get('label'):
            label = self._context.get('label')
            update_attachment_list(label)
            return attachment_list

        for label in self.label_ids:
            update_attachment_list(label)
        return attachment_list

    def print_via_printnode(self):
        user = self.env.user
        printer = user._get_shipping_label_printer()

        for ship_lab in self:
            attachment_list = ship_lab._get_attachment_list()
            if not attachment_list:
                continue
            for ascii_data, params in attachment_list:
                printer.printnode_print_b64(ascii_data, params)
                if params.get('package_id') and self.env.company.print_package_with_label:
                    report_id = self.env.company.printnode_package_report
                    if not report_id:
                        raise UserError(_(
                            'There are no available package report for printing, please, '
                            'define "Package Report to Print" in PrintNode -> Settings menu'
                        ))
                    printer.printnode_print(report_id, params.get('package_id'))


class ShippingLabelDocument(models.Model):
    """ Attached Document to the Shipping Label entity
    """
    _name = 'shipping.label.document'
    _description = 'Shipping Label Document'
    _rec_name = 'document_id'

    shipping_id = fields.Many2one(
        string='Related Shipping Label',
        comodel_name='shipping.label',
        ondelete='cascade',
    )

    document_id = fields.Many2one(
        comodel_name='ir.attachment',
        string='Shipping Label Document',
    )

    package_id = fields.Many2one(
        string='Package',
        comodel_name='stock.quant.package',
        ondelete='set null',
    )

    def print_label_with_package_via_printnode(self):
        self.shipping_id.with_context(label=self).print_via_printnode()
