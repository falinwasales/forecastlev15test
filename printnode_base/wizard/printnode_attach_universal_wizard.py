# Copyright 2021 VentorTech OU
# License OPL-1.0 or later.

from odoo import fields, models, api


class PrintnodeAttachLine(models.TransientModel):
    _name = 'printnode.attach.line'
    _description = 'Printnode Attachment Line'

    attachment_id = fields.Many2one(
        comodel_name='ir.attachment',
        string='Attachment',
    )
    name = fields.Char(
        related='attachment_id.name',
        string='Name',
    )
    bin_data = fields.Binary(
        related='attachment_id.datas',
        string='Size',
    )
    mimetype = fields.Char(
        related='attachment_id.mimetype',
        string='Type',
    )
    date = fields.Datetime(
        related='attachment_id.create_date',
        string='Creation Date',
    )
    wizard_id = fields.Many2one(
        comodel_name='printnode.attach.universal.wizard',
        string='Parent Wizard',
    )


class PrintnodeAttachUniversalWizard(models.TransientModel):
    _name = 'printnode.attach.universal.wizard'
    _description = 'Print Attachments via PrintNode'

    attach_line_ids = fields.One2many(
        comodel_name='printnode.attach.line',
        inverse_name='wizard_id',
        string='Attachments',
    )
    printer_id = fields.Many2one(
        comodel_name='printnode.printer',
        default=lambda self: self.env.user.printnode_printer.id,
        required=True,
    )

    printer_bin = fields.Many2one(
        'printnode.printer.bin',
        string='Printer Bin',
        required=False,
        domain='[("printer_id", "=", printer_id)]',
    )

    @api.onchange('printer_id')
    def _onchange_printer(self):
        """
        Reset printer_bin field to avoid bug with printing
        in wrong bin
        """
        self.printer_bin = self.printer_id.default_printer_bin.id

    def do_print(self):
        printer = self.printer_id
        for line in self.attach_line_ids:
            params = {
                'title': line.name,
                'type': 'qweb-pdf' if line.mimetype == 'application/pdf' else 'qweb-text',
                'options': {'bin': self.printer_bin.name} if self.printer_bin else {},
            }
            printer.printnode_print_b64(
                line.bin_data.decode('ascii'), params, check_printer_format=False)

    @api.model
    def default_get(self, fields_list):
        res = super(PrintnodeAttachUniversalWizard, self).default_get(fields_list)

        res_ids = self.env.context.get('active_ids')
        res_model = self.env.context.get('active_model')
        if not (res_ids and res_model):
            return res

        attachments = self.env['ir.attachment'].search([
            ('res_id', 'in', res_ids),
            ('res_model', '=', res_model),
            ('company_id', '=', self.env.company.id),
        ], order='create_date desc')
        lines_vals = [{'attachment_id': rec.id} for rec in attachments]
        attach_lines = self.env['printnode.attach.line'].create(lines_vals)
        res['attach_line_ids'] = [(6, 0, attach_lines.ids)]
        return res
