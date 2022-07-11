# Copyright 2019 VentorTech OU
# License OPL-1.0 or later.

import base64
import requests

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


REQUIRED_REPORT_KEYS = ['title', 'type', 'size']


class PrintNodeComputer(models.Model):
    """ PrintNode Computer entity
    """
    _name = 'printnode.computer'
    _description = 'PrintNode Computer'

    printnode_id = fields.Integer('Printnode ID')

    active = fields.Boolean(
        'Active',
        default=True
    )

    name = fields.Char(
        string='Name',
        size=64,
        required=True
    )

    status = fields.Char(
        string='Status',
        size=64
    )

    printer_ids = fields.One2many(
        'printnode.printer', 'computer_id',
        string='Printers'
    )

    account_id = fields.Many2one(
        'printnode.account',
        string='Account',
        ondelete='cascade',
    )

    _sql_constraints = [
        ('printnode_id', 'unique(printnode_id)', 'Computer ID should be unique.')
    ]


class PrintNodePrinter(models.Model):
    """ PrintNode Printer entity
    """
    _name = 'printnode.printer'
    _description = 'PrintNode Printer'

    printnode_id = fields.Integer('Printnode ID')

    active = fields.Boolean(
        'Active',
        default=True
    )

    online = fields.Boolean(
        string='Online',
        compute='_compute_printer_status',
        store=True,
        readonly=True
    )

    name = fields.Char(
        'Name',
        size=64,
        required=True
    )

    status = fields.Char(
        'PrintNode Status',
        size=64
    )

    printjob_ids = fields.One2many(
        'printnode.printjob', 'printer_id',
        string='Print Jobs'
    )

    paper_ids = fields.Many2many(
        'printnode.paper',
        string='Papers'
    )

    format_ids = fields.Many2many(
        'printnode.format',
        string='Formats'
    )

    computer_id = fields.Many2one(
        'printnode.computer',
        string='Computer',
        ondelete='cascade',
    )

    printer_bin_ids = fields.One2many(
        'printnode.printer.bin', 'printer_id',
        string='Printer Bins',
        readonly=True,
    )

    default_printer_bin = fields.Many2one(
        'printnode.printer.bin',
        string='Default Bin',
        required=False,
    )

    account_id = fields.Many2one(
        'printnode.account',
        string='Account',
        readonly=True,
        related='computer_id.account_id'
    )

    error = fields.Boolean(
        compute='_compute_print_rules',
    )

    notes = fields.Html(
        string='Note',
        compute='_compute_print_rules',
    )

    _sql_constraints = [
        ('printnode_id', 'unique(printnode_id)', 'Printer ID should be unique.')
    ]

    def name_get(self):
        result = []
        for printer in self:
            name = '{} ({})'.format(printer.name, printer.computer_id.name)
            result.append((printer.id, name))
        return result

    @api.depends('status', 'computer_id.status')
    def _compute_printer_status(self):
        """ check computer and printer status
        """
        for rec in self:
            rec.online = rec.status in ['online'] and \
                rec.computer_id.status in ['connected']

    def _post_printnode_job(self, uri, data):
        """ Send job into PrintNode ()
        """
        auth = requests.auth.HTTPBasicAuth(
            self.account_id.username,
            self.account_id.password or ''
        )

        ids = False

        try:
            function_name = uri.replace('/', '_')
            post_url = '{}/{}'.format(self.account_id.endpoint, uri)
            self.account_id.log_debug('%s\n%s' % (post_url, data if data else None),
                                      'printnode_post_request_%s' % function_name)
            ids = requests.post(
                post_url,
                auth=auth,
                json=data
            ).text

            self.account_id.log_debug(ids, 'printnode_post_response_%s' % function_name)
            self.sudo().write({'printjob_ids': [(0, 0, {
                'printnode_id': ids,
                'description': data['title'],
            })]})

        except Exception as e:
            raise UserError(_('Cannot send printnode job (%s).') % e)

        return ids

    def _format_title(self, objects, copies):
        if len(objects) == 1:
            return '{}_{}'.format(objects.display_name, copies)
        return '{}_{}_{}'.format(objects._description, len(objects), copies)

    def printnode_print(self, report_id, objects, copies=1, options=None):
        """ PrintNode Print
        """
        self.ensure_one()
        self.printnode_check_report(report_id)

        if not options:
            options = {}

        ids = objects.mapped('id')
        content, content_type = report_id._render(ids)

        pdf = report_id.report_type in ['qweb-pdf']

        data = {
            'printerId': self.printnode_id,
            'title': self._format_title(objects, copies),
            'source': self._get_source_name(),
            'contentType': ['raw_base64', 'pdf_base64'][pdf],
            'content': base64.b64encode(content).decode('ascii'),
            'qty': copies,
            'options': options,
        }
        return self._post_printnode_job('printjobs', data)

    def printnode_check_report(self, report_id, raise_exception=True):
        """
        """
        rp = self.env['printnode.report.policy'].search([
            ('report_id', '=', report_id.id),
        ])
        error = False

        if rp and rp.exclude_from_auto_printing:
            # We need to notify user in case he is trying to print report
            # that was excluded from printing
            error = _(
                'Your are trying to print report "{}".'
                ' But it was excluded from printing in "Report Settings" menu.'
            ).format(
                report_id.name,
            )

        report = {
            'title': rp and report_id.name,
            'type': rp and rp.report_type,
            'size': rp and rp.report_paper_id,
        }

        if not error:
            error = self.printnode_check(report)

        if error and raise_exception:
            _logger.warning('PrintNode: {}'.format(error))
            raise UserError(error)

        return error

    def printnode_check_and_raise(self, report=None):
        """
        """
        self.ensure_one()

        error = self.printnode_check(report)

        if error:
            _logger.warning('PrintNode: {}'.format(error))
            raise UserError(error)

    def printnode_check(self, report=None):
        """ PrintNode Check
            eg. report = {'type': 'qweb-pdf', 'size': <printnode.format(0,)>}
        """
        self.ensure_one()

        # 1. check user settings

        if not self.env.company.printnode_enabled:
            return _(
                'Immediate printing via PrintNode is disabled for company {}.'
                ' Please, contact Administrator to re-enable it.'
            ).format(
                self.env.company.name
            )

        # 2. check printer settings

        if self.env.company.printnode_recheck and \
                not self.sudo().account_id.recheck_printer(self.sudo()):
            return _(
                'Printer {} is not available.'
                ' Please check it for errors or select another printer.'
            ).format(
                self.name,
            )

        # 3. check report policies

        if not report:
            return

        if not (set(REQUIRED_REPORT_KEYS).issubset(set(report.keys()))):
            return _(
                'Report expected three required parameters: {}. Make sure all of them '
                'passed correctly. Report: {}.'
            ).format(
                ', '.join(REQUIRED_REPORT_KEYS),
                report,
            )

        report_types = [pf.qweb for pf in self.format_ids]

        if self.paper_ids and not report.get('size') and report.get('title'):
            return _(
                'Report {} is not properly configured (no paper size).'
                ' Please update Report Settings or choose another report.'
            ).format(
                report.get('title'),
            )

        if self.paper_ids and report.get('size') \
                and report.get('size') not in self.paper_ids:
            return _(
                'Paper size for report {} ({}) and for printer {} ({})'
                ' do not match. Please update Printer or Report Settings.'
            ).format(
                report.get('title'),
                report.get('size').name,
                self.name,
                ', '.join([p.name for p in self.paper_ids])
            )

        if report_types and report.get('type') \
                and report.get('type') not in report_types:
            formats = self.env['printnode.format'].search([
                ('qweb', '=', report.get('type'))
            ])
            return _(
                'Report type for report {} ({}) and for printer {} ({})'
                ' do not match. Please update Printer or Report Settings.'
            ).format(
                report.get('title'),
                ', '.join([f.name for f in formats]),
                self.name,
                ', '.join([p.name for p in self.format_ids])
            )

    def _get_source_name(self):
        self.env.cr.execute(
            'SELECT latest_version FROM ir_module_module WHERE name=\'printnode_base\''
        )
        result = self.env.cr.fetchone()
        full_version = result and result[0]
        split_value = full_version and full_version.split('.')
        module_version = split_value and '.'.join(split_value[-3:])
        source_name = 'Odoo Direct Print PRO %s' % module_version
        return source_name

    def printnode_print_b64(self, ascii_data, params, check_printer_format=True):
        self.ensure_one()
        error = self.printnode_check(report=(check_printer_format and params))
        if error:
            raise UserError(error)

        con_type = 'raw_base64' if params.get('type') == 'qweb-text' else 'pdf_base64'

        printnode_data = {
            'printerId': self.printnode_id,
            'qty': params.get('copies', 1),
            'title': params.get('title'),
            'source': self._get_source_name(),
            'contentType': con_type,
            'content': ascii_data,
            'options': params.get('options', {}),
        }
        return self._post_printnode_job('printjobs', printnode_data)

    @api.depends('paper_ids', 'format_ids')
    def _compute_print_rules(self):

        def _html(message, icon='fa fa-question-circle-o'):
            return '<span class="{}" title="{}"></span>'.format(icon, message)

        def _ok(message):
            return False, _html(message, 'fa fa-circle-o')

        def _error(message):
            return True, _html(message, 'fa fa-exclamation-circle')

        for printer in self:

            reports = self.env['printnode.rule'].search([
                ('printer_id', '=', printer.id)
            ]).mapped('report_id')

            errors = list(set(filter(None, [
                printer.printnode_check_report(report, False)
                for report in reports
            ] + [printer.printnode_check()])))

            if errors:
                printer.error, printer.notes = _error('\n'.join(errors))
            else:
                printer.error, printer.notes = _ok(_('Configuration is valid.'))


class PrintNodePaper(models.Model):
    """ PrintNode Paper entity
    """
    _name = 'printnode.paper'
    _description = 'PrintNode Paper'

    name = fields.Char(
        'Name',
        size=64,
        required=True
    )

    width = fields.Integer('Width')

    height = fields.Integer('Height')


class PrintNodeFormat(models.Model):
    """ PrintNode Content Type
    """
    _name = 'printnode.format'
    _description = 'PrintNode Format'

    name = fields.Char(
        'Content Type',
        size=8,
        required=True
    )

    qweb = fields.Char(
        'QWeb Name',
        size=16,
        required=True
    )


class PrinterBin(models.Model):
    """ PrintNode Printer Bin
    """
    _name = 'printnode.printer.bin'
    _description = 'PrintNode Printer Bin'

    name = fields.Char(
        'Bin Name',
        required=True,
    )

    printer_id = fields.Many2one(
        'printnode.printer',
        string='Printer',
        required=True,
        ondelete='cascade',
    )


class PrintNodePrintJob(models.Model):
    """ PrintNode Job entity
    """

    _name = 'printnode.printjob'
    _description = 'PrintNode Job'

    printnode_id = fields.Integer('Printnode ID')

    printer_id = fields.Many2one(
        'printnode.printer',
        string='Printer',
        ondelete='cascade',
    )

    description = fields.Char(
        string='Label',
        size=64
    )

    _sql_constraints = []
