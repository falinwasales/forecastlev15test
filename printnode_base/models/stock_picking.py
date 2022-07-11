# Copyright 2019 VentorTech OU
# License OPL-1.0 or later.

from odoo import models, fields, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'multi.print.mixin', 'printnode.scenario.mixin']

    shipping_label_ids = fields.One2many(
        comodel_name='shipping.label',
        inverse_name='picking_id',
        string='Shipping Labels',
    )

    def button_validate(self):
        res = super(StockPicking, self).button_validate()

        if res is True:
            printed = self.print_scenarios(action='print_document_on_transfer')

            if printed:
                self.write({'printed': True})

            # Print product labels
            self.print_scenarios(action='print_product_labels_on_transfer')

            # Print packages
            self.print_scenarios(action='print_packages_label_on_transfer')

        return res

    def cancel_shipment(self):
        """ Redefining a standard method
        """
        for stock_pick in self:
            shipping_label = stock_pick.shipping_label_ids.filtered(
                lambda sl: sl.tracking_numbers == self.carrier_tracking_ref
            )
            shipping_label.write({'label_status': 'inactive'})
        return super(StockPicking, self).cancel_shipment()

    def print_last_shipping_label(self):
        self.ensure_one()

        if self.picking_type_code != 'outgoing':
            return

        label = self.shipping_label_ids[:1]
        if not (label and label.label_ids and label.label_status == 'active'):
            if not self.env.company.print_sl_from_attachment:
                raise UserError(_(
                    'There are no available "shipping labels" for printing, '
                    'or last "shipping label" in state "In Active"'
                ))
            return self._print_sl_from_attachment(self.env.context.get('raise_exception_slp', True))
        return label.print_via_printnode()

    def send_to_shipper(self):
        """ Redefining a standard method
        """
        user = self.env.user

        auto_print = user.company_id.auto_send_slp and \
            user.company_id.printnode_enabled and user.printnode_enabled

        if auto_print and user.company_id.print_package_with_label:
            if self.picking_type_id == self.picking_type_id.warehouse_id.out_type_id:
                move_lines_without_package = self.move_line_ids_without_package.filtered(
                    lambda l: not l.result_package_id)
                if move_lines_without_package:
                    raise UserError(_('Some products on Delivery Order are not in Package. For '
                                      'printing Package Slips + Shipping Labels, please, put in '
                                      'pack remaining products. If you want to print only Shipping '
                                      'Label, please, deactivate "Print Package just after Shipping'
                                      ' Label" checkbox in PrintNode/Configuration/Settings'))

        if auto_print:
            # Expected UserError if there is no shipping label printer is available.
            user._get_shipping_label_printer()

        super(StockPicking, self).send_to_shipper()

        tracking_ref = self.carrier_tracking_ref
        if not tracking_ref:
            return
        messages_to_parse = self.env['mail.message'].search([
            ('model', '=', 'stock.picking'),
            ('res_id', '=', self.id),
            ('message_type', '=', 'notification'),
            ('attachment_ids', '!=', False),
            ('body', 'ilike', tracking_ref),
        ])
        for message in messages_to_parse:
            self._create_shipping_label(message)

        if auto_print and (self.shipping_label_ids or user.company_id.print_sl_from_attachment):
            self.with_context(raise_exception_slp=False).print_last_shipping_label()

    def _add_multi_print_lines(self):
        product_lines = []
        unit_uom = self.env.ref('uom.product_uom_unit')
        for move in self.move_lines:
            quantity = 1
            if move.product_uom == unit_uom:
                quantity = move.product_uom_qty

            product_lines.append(
                (0, 0, {
                    'product_id': move.product_id.id,
                    'quantity': quantity},
                 )
            )
        return product_lines

    def _print_sl_from_attachment(self, raise_exception=True):
        self.ensure_one()

        domain = [
            ('res_id', '=', self.id),
            ('res_model', '=', self._name),
            ('company_id', '=', self.company_id.id),
        ]

        attachment = self.env['ir.attachment'].search(
            domain, order='create_date desc', limit=1
        )
        if not attachment:
            if raise_exception:
                raise UserError(_(
                    'There are no attachments in the current Transfer.'
                ))
            return

        domain.append(('create_date', '=', attachment.create_date))
        last_attachments = self.env['ir.attachment'].search(domain)

        printer = self.env.user._get_shipping_label_printer()

        for doc in last_attachments:
            params = {
                'title': doc.name,
                'type': 'qweb-pdf' if doc.mimetype == 'application/pdf' else 'qweb-text',
            }
            printer.printnode_print_b64(
                doc.datas.decode('ascii'), params, check_printer_format=False)

    def _create_backorder(self):
        backorders = super(StockPicking, self)._create_backorder()

        if backorders:
            printed = self.print_scenarios(
                action='print_document_on_backorder',
                ids_list=backorders.mapped('id'))

            if printed:
                backorders.write({'printed': True})

        return backorders

    def _create_shipping_label(self, message):
        label_attachments = []
        if len(self.package_ids) == len(message.attachment_ids):
            for index in range(len(self.package_ids)):
                vals = {
                    'document_id': message.attachment_ids[-index - 1].id,
                    'package_id': self.package_ids[index].id
                }
                label_attachments.append((0, 0, vals))
        else:
            label_attachments = [
                (0, 0, {'document_id': attach.id}) for attach in message.attachment_ids
            ]
        shipping_label_vals = {
            'carrier_id': self.carrier_id.id,
            'picking_id': self.id,
            'tracking_numbers': self.carrier_tracking_ref,
            'label_ids': label_attachments,
            'label_status': 'active',
        }
        self.env['shipping.label'].create(shipping_label_vals)

    def _scenario_print_product_labels_on_transfer(
        self, report_id, printer_id, number_of_copies=1, **kwargs
    ):
        """
        Special method to provide custom logic of printing
        (like printing labels through wizards).

        If you need to just print a report - check scenarios.
        """
        product_lines = self._add_multi_print_lines()

        wizard = self.env['product.label.multi.print'].create({
            'report_id': report_id.id,
            'product_line_ids': product_lines,
        })

        wizard.do_print()

        return True

    def _scenario_print_single_lot_label_on_transfer(
        self, report_id, printer_id, number_of_copies=1, **kwargs
    ):
        """
        Print single lot label for each move line
        """
        new_move_lines = kwargs.get('new_move_lines')
        print_options = kwargs.get('options', {})
        move_lines_with_lots_and_qty_done = new_move_lines.filtered(
            lambda ml: ml.lot_id and not ml.printnode_printed and ml.qty_done > 0)

        printed = False

        for move_line in move_lines_with_lots_and_qty_done:
            if move_line.lot_id:
                printer_id.printnode_print(
                    report_id,
                    move_line.lot_id,
                    copies=number_of_copies,
                    options=print_options,
                )

                move_line.write({'printnode_printed': True})
                printed = True

        return printed

    def _scenario_print_multiple_lot_labels_on_transfer(
        self, report_id, printer_id, number_of_copies=1, **kwargs
    ):
        """
        Print multiple lot labels (depends on quantity) for each move line
        """
        new_move_lines = kwargs.get('new_move_lines')
        print_options = kwargs.get('options', {})
        move_lines_with_lots_and_qty_done = new_move_lines.filtered(
            lambda ml: ml.lot_id and not ml.printnode_printed and ml.qty_done > 0)

        printed = False

        for move_line in move_lines_with_lots_and_qty_done:
            lots = self.env['stock.production.lot']

            for i in range(int(move_line.qty_done)):
                lots = lots.concat(move_line.lot_id)

            if lots:
                printer_id.printnode_print(
                    report_id,
                    lots,
                    copies=number_of_copies,
                    options=print_options,
                )

                move_line.write({'printnode_printed': True})
                printed = True

        return printed

    def _scenario_print_single_product_label_on_transfer(
        self, report_id, printer_id, number_of_copies=1, **kwargs
    ):
        """
        Print single product label for each move line
        """
        new_move_lines = kwargs.get('new_move_lines')
        print_options = kwargs.get('options', {})

        move_lines_with_qty_done = new_move_lines.filtered(
            lambda ml: not ml.printnode_printed and ml.qty_done > 0)

        printed = False

        for move_line in move_lines_with_qty_done:
            printer_id.printnode_print(
                report_id,
                move_line.product_id,
                copies=number_of_copies,
                options=print_options,
            )

            move_line.write({'printnode_printed': True})
            printed = True

        return printed

    def _scenario_print_multiple_product_labels_on_transfer(
        self, report_id, printer_id, number_of_copies=1, **kwargs
    ):
        """
        Print multiple product labels for each move line
        """
        new_move_lines = kwargs.get('new_move_lines')
        print_options = kwargs.get('options', {})
        move_lines_with_qty_done = new_move_lines.filtered(
            lambda ml: not ml.printnode_printed and ml.qty_done > 0)

        unit_uom = self.env.ref('uom.product_uom_unit')

        printed = False

        for move_line in move_lines_with_qty_done:
            products = self.env['product.product']

            quantity = 1
            if move_line.product_uom_id == unit_uom:
                quantity = int(move_line.qty_done)

            for i in range(quantity):
                products = products.concat(move_line.product_id)

            if products:
                printer_id.printnode_print(
                    report_id,
                    products,
                    copies=number_of_copies,
                    options=print_options,
                )

                move_line.write({'printnode_printed': True})
                printed = True

        return printed

    def _scenario_print_packages_label_on_transfer(
        self, report_id, printer_id, number_of_copies=1, **kwargs
    ):
        packages = self.mapped('package_ids')
        print_options = kwargs.get('options', {})
        printer_id.printnode_print(
            report_id,
            packages,
            copies=number_of_copies,
            options=print_options,
        )
