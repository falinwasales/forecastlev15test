# Copyright 2019 VentorTech OU
# License OPL-1.0 or later.

from odoo import models, fields, _
from odoo.exceptions import UserError


class User(models.Model):
    """ User entity. Add 'Default Printer' field (no restrictions).
    """
    _inherit = 'res.users'

    printnode_enabled = fields.Boolean(
        string='Print via PrintNode',
        default=False,
    )

    printnode_printer = fields.Many2one(
        'printnode.printer',
        string='Default Printer',
    )

    user_label_printer = fields.Many2one(
        'printnode.printer',
        string='Shipping Label Printer',
    )

    printnode_rule_ids = fields.One2many(
        comodel_name='printnode.rule',
        inverse_name='user_id',
        string='Printnode Rules',
    )

    def __init__(self, pool, cr):
        # pylint: disable=return-in-init
        """
        Adding access rights on printnode related fields on user form
        """

        readable_fields = ['printnode_enabled',
                           'printnode_printer',
                           'user_label_printer',
                           'printnode_rule_ids']
        writable_fields = ['printnode_enabled',
                           'printnode_printer',
                           'user_label_printer']

        init_res = super().__init__(pool, cr)
        type(self).SELF_READABLE_FIELDS = type(self).SELF_READABLE_FIELDS + readable_fields
        print('===========================================================================')
        print(type(self).SELF_READABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS = type(self).SELF_WRITEABLE_FIELDS + writable_fields
        return init_res

    def _get_shipping_label_printer(self):
        company = self.company_id

        printer = self.user_label_printer or company.company_label_printer
        if not printer:
            raise UserError(_(
                'Neither on company level, no on user level default label printer '
                'is defined. Please, define it.'
            ))
        return printer

    def _get_report_printer(self, report_id):
        self.ensure_one()
        rule = self.printnode_rule_ids.filtered(lambda r: r.report_id.id == report_id)[:1]
        printer = rule.printer_id or self.printnode_printer or self.company_id.printnode_printer
        printer_bin = rule.printer_bin if rule.printer_id else printer.default_printer_bin
        return printer, printer_bin
