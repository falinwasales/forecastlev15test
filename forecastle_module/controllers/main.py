# Copyright 2019 VentorTech OU
# License OPL-1.0 or later.

import json
from copy import deepcopy

from odoo.addons.web.controllers.main import DataSet, ReportController

from odoo import http
from odoo.http import request, content_disposition
from odoo.http import serialize_exception as _serialize_exception
from odoo.tools import html_escape
from odoo.tools.translate import _
from odoo import http, api
from werkzeug.exceptions import ImATeapot
import io
import xlsxwriter
from datetime import datetime
from io import BytesIO
from urllib.request import urlopen
import base64
from datetime import date




SECURITY_GROUP = 'printnode_base.printnode_security_group_user'
PDF = ['qweb-pdf']
RAW = ['qweb-text']

# we use this dummy exception to clearly differentiate
# printnode exception in ajax response for downloading report
class PrintNodeSuccess(ImATeapot):
    pass

class ReportControllerProxy(ReportController):

    @http.route('/report/download', type='http', auth="user")
    def report_download(self, data, context=None):
        """ print reports on report_download
        """
        user = request.env.user
        if not user.has_group(SECURITY_GROUP) \
                or not request.env.company.printnode_enabled or not user.printnode_enabled:
            return super(ReportControllerProxy, self).report_download(data, context)

        requestcontent = json.loads(data)

        if len(requestcontent) > 2 and requestcontent[2]:
            # download only
            return super(ReportControllerProxy, self).report_download(data, context)

        if requestcontent[1] not in PDF + RAW:
            return super(ReportControllerProxy, self).report_download(data, context)

        ext = requestcontent[1].split('-')[1]
        report_name, object_ids = requestcontent[0].\
            split('/report/{}/'.format(ext))[1].split('?')[0].split('/')

        report_id = request.env['ir.actions.report']._get_report_from_name(report_name)

        rp = request.env['printnode.report.policy'].search([
            ('report_id', '=', report_id.id),
        ])

        if rp and rp.exclude_from_auto_printing:
            # If report is excluded from printing, than just download it
            return super(ReportControllerProxy, self).report_download(data, context)

        printer_id, printer_bin = user._get_report_printer(report_id.id)

        if not printer_id:
            return super(ReportControllerProxy, self).report_download(data, context)

        try:
            ids = [int(x) for x in object_ids.split(',')]
            obj = request.env[report_id.model].browse(ids)
            options = {'bin': printer_bin} if printer_bin else {}

            printer_id.printnode_print(report_id, obj, copies=9, options=options)

        except Exception as e:
            return request.make_response(html_escape(json.dumps({
                'code': 200,
                'message': 'Odoo Server Error',
                'data': _serialize_exception(e),
            })))

        index = user.company_id.im_a_teapot
        raise PrintNodeSuccess(['', _('Sent to PrintNode')][index])
