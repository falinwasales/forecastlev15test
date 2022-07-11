# Copyright 2019 VentorTech OU
# License OPL-1.0 or later.

from odoo import fields, models, api

REPORT_DOMAIN = [
    ('model', '=', 'product.product'),
    ('report_type', 'in', ['qweb-pdf', 'qweb-text']),
]


class Company(models.Model):
    _inherit = 'res.company'

    printnode_enabled = fields.Boolean(
        string='Print via PrintNode',
        default=False,
    )

    printnode_printer = fields.Many2one(
        'printnode.printer',
        string='Printer',
    )

    printnode_recheck = fields.Boolean(
        string='Mandatory check Printing Status',
        default=False,
    )

    company_label_printer = fields.Many2one(
        'printnode.printer',
        string='Shipping Label Printer',
    )

    auto_send_slp = fields.Boolean(
        string='Auto-send to Shipping Label Printer',
        default=False,
    )

    print_sl_from_attachment = fields.Boolean(
        string='(Experimental) Use Attachments Printing for Shipping Label(s)',
        default=False,
    )

    im_a_teapot = fields.Boolean(
        string='Show success notifications',
        default=True,
    )

    wizard_report_ids = fields.Many2many(
        'ir.actions.report',
        string='Available Reports',
        domain=REPORT_DOMAIN,
    )

    def_wizard_report_id = fields.Many2one(
        'ir.actions.report',
        string='Default Report',
    )

    printnode_notification_email = fields.Char(
        string="PrintNode Notification Email",
    )

    printnode_notification_page_limit = fields.Integer(
        string="PrintNode Notification Page Limit",
        default=100,
    )

    print_package_with_label = fields.Boolean(
        string='Print Package just after Shipping Label',
        default=False,
    )

    printnode_package_report = fields.Many2one(
        'ir.actions.report',
        string='Package Report to Print',
    )


class Settings(models.TransientModel):
    _inherit = 'res.config.settings'

    printnode_enabled = fields.Boolean(
        readonly=False,
        related='company_id.printnode_enabled',
    )

    printnode_printer = fields.Many2one(
        'printnode.printer',
        readonly=False,
        related='company_id.printnode_printer',
    )

    printnode_recheck = fields.Boolean(
        readonly=False,
        related='company_id.printnode_recheck',
    )

    company_label_printer = fields.Many2one(
        'printnode.printer',
        readonly=False,
        related='company_id.company_label_printer',
    )

    auto_send_slp = fields.Boolean(
        readonly=False,
        related='company_id.auto_send_slp',
    )

    print_sl_from_attachment = fields.Boolean(
        readonly=False,
        related='company_id.print_sl_from_attachment',
    )

    im_a_teapot = fields.Boolean(
        readonly=False,
        related='company_id.im_a_teapot',
    )

    wizard_report_ids = fields.Many2many(
        readonly=False,
        related='company_id.wizard_report_ids',
    )

    wizard_report_domain_ids = fields.Many2many(
        'ir.actions.report',
        compute='_compute_wizard_report_domain_ids',
        store=False,
    )

    def_wizard_report_id = fields.Many2one(
        readonly=False,
        related='company_id.def_wizard_report_id',
        domain="[('id', 'in', wizard_report_domain_ids)]",
    )

    printnode_notification_email = fields.Char(
        readonly=False,
        related='company_id.printnode_notification_email',
    )

    printnode_notification_page_limit = fields.Integer(
        readonly=False,
        related='company_id.printnode_notification_page_limit',
    )

    print_package_with_label = fields.Boolean(
        readonly=False,
        related='company_id.print_package_with_label',
    )

    printnode_package_report = fields.Many2one(
        readonly=False,
        related='company_id.printnode_package_report',
    )

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(Settings, self).fields_get()
        available_report_ids = self.env.company.wizard_report_ids.ids
        if available_report_ids:
            res['def_wizard_report_id']['domain'] = [('id', 'in', available_report_ids)]
        return res

    @api.depends('wizard_report_ids')
    def _compute_wizard_report_domain_ids(self):
        for record in self:
            if record.wizard_report_ids:
                record.wizard_report_domain_ids = record.wizard_report_ids
            else:
                record.wizard_report_domain_ids = \
                    self.env['ir.actions.report'].search(REPORT_DOMAIN)

    @api.onchange('wizard_report_ids')
    def _onchange_available_wizard_report(self):
        available_report_ids = self.wizard_report_ids.ids

        if not available_report_ids:
            self.def_wizard_report_id = False
        elif self.def_wizard_report_id and self.def_wizard_report_id.id not in available_report_ids:
            self.def_wizard_report_id = available_report_ids[0]

    @api.onchange('print_package_with_label', 'print_sl_from_attachment')
    def _onchange_print_package_with_label(self):
        if self.print_package_with_label:
            self.print_sl_from_attachment = False
        if self.print_sl_from_attachment:
            self.print_package_with_label = False

    def set_values(self):
        if self.print_package_with_label and not self.group_stock_tracking_lot:
            self.group_stock_tracking_lot = True
        super(Settings, self).set_values()
