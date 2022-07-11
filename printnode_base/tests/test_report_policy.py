# Copyright 2019 VentorTech OU
# License OPL-1.0 or later.
from odoo.exceptions import UserError, ValidationError
from odoo.tests import common, tagged
from odoo.tools import mute_logger
from random import randint
from unittest.mock import patch


SECURITY_GROUP = 'printnode_base.printnode_security_group_user'


@tagged('post_install', '-at_install')
class TestPrintNodeReport(common.TransactionCase):

    def setUp(self):
        super(TestPrintNodeReport, self).setUp()

        self.company = self.env.ref('base.main_company')
        self.company.printnode_recheck = False

        self.user = self.env['res.users'].with_context({
            'no_reset_password': True
        }).create({
            'name': 'Printnode User',
            'company_id': self.company.id,
            'login': 'user',
            'email': 'user@print.node',
            'groups_id': [(6, 0, [
                self.env.ref(SECURITY_GROUP).id
            ])]
        })

        # report

        self.report = self.env['ir.actions.report'].create({
            'name': 'Model Overview',
            'model': 'ir.model',
            'report_type': 'qweb-pdf',
            'report_name': 'base.report_irmodeloverview',
        })

        # device

        self.account = self.env['printnode.account'].create({
            'username': 'apikey'
        })
        self.computer = self.env['printnode.computer'].create({
            'name': 'Local Computer',
            'status': 'connected',
            'account_id': self.account.id,
        })
        self.printer = self.env['printnode.printer'].create({
            'name': 'Local Printer',
            'status': 'offline',
            'computer_id': self.computer.id,
        })
        self.policy = self.env['printnode.report.policy'].create({
            'report_id': self.report.id,
        })
        self.so_model = self.env['ir.model'].search([('model', '=', 'sale.order')])
        self.so_report = self.env['ir.actions.report'].search([
            ('name', '=', 'Quotation / Order'),
        ])
        self.action_method = self._get_or_create_action_confirm()
        self.action_button = self.env['printnode.action.button'].create({
            'model_id': self.so_model.id,
            'method_id': self.action_method.id,
            'description': 'Print SO by confirm button',
            'report_id': self.so_report.id,
        })
        self.user_rule = self.env['printnode.rule'].create({
            'user_id': self.user.id,
            'printer_id': self.printer.id,
            'report_id': self.so_report.id,
        })
        self.del_slip_rep = self.env['ir.actions.report'].search([
            ('name', '=', 'Delivery Slip'),
        ])

    def _get_or_create_action_confirm(self):
        method = self.env['printnode.action.method'].search([
            ('model_id', '=', self.so_model.id),
            ('method', '=', 'action_confirm'),
        ])
        if not method:
            method = self.env['printnode.action.method'].create({
                'name': 'SO Print',
                'model_id': self.so_model.id,
                'method': 'action_confirm',
            })
        return method

    def _add_printers(self):
        company_printer = self.env['printnode.printer'].create({
            'name': 'Company Printer',
            'status': 'online',
            'computer_id': self.computer.id,
        })
        user_printer = self.env['printnode.printer'].create({
            'name': 'User Printer',
            'status': 'online',
            'computer_id': self.computer.id,
        })
        action_printer = self.env['printnode.printer'].create({
            'name': 'Action Printer',
            'status': 'online',
            'computer_id': self.computer.id,
        })
        return company_printer, user_printer, action_printer

    def _up_multiprint_wizard(self, object_):
        wizard_action = object_.open_product_label_multi_print_wizard()
        self.assertEqual(wizard_action.get('type'), 'ir.actions.act_window')
        wizard_model = wizard_action.get('res_model')
        self.assertEqual(wizard_model, 'product.label.multi.print')
        wizard_id = wizard_action.get('res_id')
        return self.env[wizard_model].browse(wizard_id)

    @mute_logger('odoo.addons.printnode_base.models.printnode_device')
    def test_printnode_module_disabled(self):
        self.company.printnode_enabled = False

        with self.assertRaises(UserError), self.cr.savepoint():
            self.printer.with_user(self.user.id).printnode_check_and_raise()

    @mute_logger('odoo.addons.printnode_base.models.printnode_device')
    def test_printnode_recheck(self):
        self.company.printnode_enabled = True
        self.company.printnode_recheck = True

        with self.assertRaises(UserError), self.cr.savepoint(), \
                patch.object(type(self.account), 'recheck_printer', return_value=False):
            self.printer.with_user(self.user.id).printnode_check_and_raise()

    def test_printnode_no_recheck(self):
        self.company.printnode_enabled = True

        self.printer.with_user(self.user.id).printnode_check_and_raise()

    def test_printnode_policy_report_no_size_and_printer_no_size(self):
        self.company.printnode_enabled = True

        self.policy.report_paper_id = None
        self.printer.paper_ids = [(5, 0, 0)]

        self.printer.with_user(self.user.id).printnode_check_report(self.report)

    @mute_logger('odoo.addons.printnode_base.models.printnode_device')
    def test_printnode_policy_report_no_size_and_printer_size(self):
        self.company.printnode_enabled = True

        self.policy.report_paper_id = None
        self.printer.paper_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_paper_a4').id])]

        with self.assertRaises(UserError), self.cr.savepoint():
            self.printer.with_user(self.user.id).printnode_check_report(self.report)

    @mute_logger('odoo.addons.printnode_base.models.printnode_device')
    def test_printnode_policy_report_size_and_printer_no_size(self):
        self.company.printnode_enabled = True

        self.policy.report_paper_id = \
            self.env.ref('printnode_base.printnode_paper_a6')
        self.printer.paper_ids = [(5, 0, 0)]

        self.printer.with_user(self.user.id).printnode_check_report(self.report)

    @mute_logger('odoo.addons.printnode_base.models.printnode_device')
    def test_printnode_policy_report_size_not_eq_printer_size(self):
        self.company.printnode_enabled = True

        self.policy.report_paper_id = \
            self.env.ref('printnode_base.printnode_paper_a6')
        self.printer.paper_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_paper_a4').id])]

        with self.assertRaises(UserError), self.cr.savepoint():
            self.printer.with_user(self.user.id).printnode_check_report(self.report)

    def test_printnode_policy_report_size_eq_printer_size(self):
        self.company.printnode_enabled = True

        self.policy.report_paper_id = \
            self.env.ref('printnode_base.printnode_paper_a6')
        self.printer.paper_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_paper_a6').id])]

        self.printer.with_user(self.user.id).printnode_check_report(self.report)

    @mute_logger('odoo.addons.printnode_base.models.printnode_device')
    def test_printnode_policy_report_type_and_printer_no_type(self):
        self.company.printnode_enabled = True

        self.policy.report_type = 'qweb-pdf'
        self.printer.format_ids = [(5, 0, 0)]

        self.printer.with_user(self.user.id).printnode_check_report(self.report)

    @mute_logger('odoo.addons.printnode_base.models.printnode_device')
    def test_printnode_policy_report_type_not_eq_printer_type(self):
        self.company.printnode_enabled = True

        self.policy.report_type = 'qweb-pdf'
        self.printer.format_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_content_type_raw').id])]

        with self.assertRaises(UserError), self.cr.savepoint():
            self.printer.with_user(self.user.id).printnode_check_report(self.report)

    def test_printnode_policy_report_type_eq_printer_type(self):
        self.company.printnode_enabled = True

        self.policy.report_type = 'qweb-pdf'
        self.printer.format_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_content_type_pdf').id])]

        self.printer.with_context(user=self.user).printnode_check_report(self.report)

    @mute_logger('odoo.addons.printnode_base.models.printnode_device')
    def test_printnode_policy_attachment_wrong_type(self):
        self.company.printnode_enabled = True

        self.printer.paper_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_paper_a4').id])]
        self.printer.format_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_content_type_raw').id])]

        with self.assertRaises(UserError), self.cr.savepoint():
            self.printer.with_user(self.user.id).printnode_check_and_raise({
                'title': 'Label',
                'type': 'qweb-pdf',
                'size': self.env.ref('printnode_base.printnode_paper_a4'),
            })

    @mute_logger('odoo.addons.printnode_base.models.printnode_device')
    def test_printnode_policy_attachment_wrong_size(self):
        self.company.printnode_enabled = True

        self.printer.paper_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_paper_a6').id])]
        self.printer.format_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_content_type_pdf').id])]

        with self.assertRaises(UserError), self.cr.savepoint():
            self.printer.with_user(self.user.id).printnode_check_and_raise({
                'title': 'Label',
                'type': 'qweb-pdf',
                'size': self.env.ref('printnode_base.printnode_paper_a4'),
            })

    @mute_logger('odoo.addons.printnode_base.models.printnode_device')
    def test_printnode_policy_attachment_empty_params(self):
        self.company.printnode_enabled = True

        self.printer.paper_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_paper_a4').id])]
        self.printer.format_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_content_type_pdf').id])]

        with self.assertRaises(UserError):
            self.printer.with_user(self.user.id).printnode_check_and_raise({
                'title': 'Label',
            })

    def test_printnode_policy_attachment_valid_params(self):
        self.company.printnode_enabled = True

        self.printer.paper_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_paper_a4').id])]
        self.printer.format_ids = [(6, 0, [
            self.env.ref('printnode_base.printnode_content_type_pdf').id])]

        self.printer.with_user(self.user.id).printnode_check_and_raise({
            'title': 'Label',
            'type': 'qweb-pdf',
            'size': self.env.ref('printnode_base.printnode_paper_a4'),
        })

    def test_action_domain(self):
        self.partner_1 = self.env['res.partner'].create({'name': 'Printnode Partner1'})
        self.partner_2 = self.env['res.partner'].create({'name': 'Printnode Partner2'})
        self.sl_order = self.env['sale.order'].create({'partner_id': self.partner_1.id})

        # Empty action domain
        self.assertEqual(self.action_button.domain, '[]')
        objects = self.action_button._get_model_objects(self.sl_order.ids)
        self.assertEqual(objects, self.sl_order)

        # Set action domain for 'partner_1' (partner for 'sl_order')
        self.action_button.domain = '[["partner_id", "=", %s]]' % self.partner_1.id
        objects = self.action_button._get_model_objects(self.sl_order.ids)
        self.assertEqual(objects, self.sl_order)

        # Set action domain for 'partner_2'. Sale Order will be filtered.
        self.action_button.domain = '[["partner_id", "=", %s]]' % self.partner_2.id
        objects = self.action_button._get_model_objects(self.sl_order.ids)
        self.assertFalse(objects)

    def test_raise_product_product_multi_printing_wizard(self):
        self.env.user.printnode_printer = self.printer

        prod_prod = self.env['product.product'].create({
            'name': 'product_variant_1',
        })
        wizard = self._up_multiprint_wizard(prod_prod)

        self.assertEqual(self.env.user.printnode_printer.id, wizard.printer_id.id)

        self.assertEqual(len(wizard.product_line_ids), 1)

        product_line = wizard.product_line_ids
        self.assertEqual(product_line.product_id.id, prod_prod.id)

        self.assertEqual(product_line.quantity, 1)

        with self.assertRaises(ValidationError):
            product_line.write({'quantity': 0})

    def test_raise_product_template_multi_printing_wizard(self):
        self.env.user.printnode_printer = self.printer

        prod_tmpl = self.env['product.template'].create({
            'name': 'product_template_1',
        })
        wizard = self._up_multiprint_wizard(prod_tmpl)

        self.assertEqual(self.env.user.printnode_printer.id, wizard.printer_id.id)

        self.assertEqual(len(wizard.product_line_ids), 1)

        product_line = wizard.product_line_ids
        related_prod_prod = prod_tmpl.product_variant_ids
        self.assertEqual(product_line.product_id.id, related_prod_prod.id)

        self.assertEqual(product_line.quantity, 1)

        with self.assertRaises(ValidationError):
            product_line.write({'quantity': 0})

    def test_raise_stock_picking_multi_printing_wizard(self):
        products = []
        total_qty = 0
        self.env.user.printnode_printer = self.printer

        for i in range(1, 6):
            product = self.env['product.product'].create({
                'name': 'product_{}'.format(i),
                'type': 'product',
            })
            qty = randint(1, 5)
            total_qty += qty
            products.append((product, qty))

        self.customer = self.env['res.partner'].create({
            'name': 'Customer',
        })
        self.sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'order_line':
                [(0, 0, {'product_id': prod.id, 'product_uom_qty': qty}) for prod, qty in products],
        })
        self.sale_order.action_confirm()

        wh_out = self.sale_order.picking_ids[:1]
        wizard = self._up_multiprint_wizard(wh_out)

        self.assertEqual(self.env.user.printnode_printer.id, wizard.printer_id.id)

        self.assertEqual(len(wizard.product_line_ids), len(products))

        self.assertEqual(len(wizard.get_docids()), total_qty)

        product_lines = wizard.product_line_ids

        for line in product_lines:
            with self.assertRaises(ValidationError):
                line.write({'quantity': 0})

    def test_get_printer_for_action_button(self):
        company_printer, user_printer, action_printer = self._add_printers()

        self.company.write({'printnode_printer': company_printer.id})
        self.user.write({'printnode_printer': user_printer.id})
        self.action_button.write({'printer_id': action_printer.id})

        # Expected ActionButton Printer
        printer, printer_bin = self.action_button.with_user(self.user.id)._get_action_printer()
        self.assertEqual(printer.id, action_printer.id)

        # Expected UserRule Printer
        self.action_button.write({'printer_id': False})
        printer, printer_bin = self.action_button.with_user(self.user.id)._get_action_printer()
        self.assertEqual(printer.id, self.user_rule.printer_id.id)

        # Expected User's Printer
        self.user_rule.write({'report_id': self.del_slip_rep.id})
        printer, printer_bin = self.action_button.with_user(self.user.id)._get_action_printer()
        self.assertEqual(printer.id, self.user.printnode_printer.id)

        # Expected Company's Printer
        self.user.write({'printnode_printer': False})
        printer, printer_bin = self.action_button.with_user(self.user.id)._get_action_printer()
        self.assertEqual(printer.id, self.company.printnode_printer.id)

    def test_get_printer_within_report_download(self):
        company_printer, user_printer, _ = self._add_printers()

        self.company.write({'printnode_printer': company_printer.id})
        self.user.write({'printnode_printer': user_printer.id})

        # Expected UserRule Printer
        self.action_button.write({'printer_id': False})
        printer, printer_bin = self.user._get_report_printer(self.so_report.id)
        self.assertEqual(printer.id, self.user_rule.printer_id.id)

        # Expected User's Printer
        self.user_rule.write({'report_id': self.del_slip_rep.id})
        printer, printer_bin = self.user._get_report_printer(self.so_report.id)
        self.assertEqual(printer.id, self.user.printnode_printer.id)

        # Expected Company's Printer
        self.user.write({'printnode_printer': False})
        printer, printer_bin = self.user._get_report_printer(self.so_report.id)
        self.assertEqual(printer.id, self.company.printnode_printer.id)
