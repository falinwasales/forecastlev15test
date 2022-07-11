# -*- coding: utf-8 -*-
# © 2015 Gael Rabier, Pierre Faniel, Jérôme Guerriat
# © 2015 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import base64
import logging
import os
import tempfile

import io
from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval as eval
from PyPDF2 import PdfFileWriter, PdfFileReader
import os.path
from ast import literal_eval
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _get_drawing_template(self, res_ids, data, drawing_report):
        templates = False

        if drawing_report:
            for draw in drawing_report:
                model = draw.model
                active_ids = ['id', 'in', res_ids]
                domain = []
                if draw.domain:
                    domain = literal_eval(draw.domain)
                domain.append(active_ids)

                records = False
                try:
                    records = self.env[model].search(domain)
                except ValueError:
                    raise UserError(_("Error domain on drawing %s") % draw.drawing_template_id.name)

                if records:
                    if templates:
                        templates |= draw.drawing_template_id
                    else:
                        templates = draw.drawing_template_id
        return templates

    def _render_qweb_pdf(self, res_ids=None, data=None):
        drawing_report = self.sudo().env['fal.drawing.report'].search([('report_id', '=', self.id)])

        if drawing_report:
            if len(res_ids) > 1:
                temporary_files = []
                for docid in res_ids:
                    report_pdf = super(IrActionsReport, self)._render_qweb_pdf(
                        [docid], data)
                    drawing_template = self._get_drawing_template([docid], data, drawing_report)
                    pdf_incl_terms = self.add_drawing(
                        docid, report_pdf, drawing_template)

                    pdfreport_fd, pdfreport_path = tempfile.mkstemp(
                        suffix='.pdf', prefix='report.tmp.')
                    os.write(pdfreport_fd, pdf_incl_terms[0])
                    os.close(pdfreport_fd)

                    temporary_files.append(pdfreport_path)

                pdf_writer = PdfFileWriter()
                for path in temporary_files:
                    pdf_reader = PdfFileReader(path)
                    for page in range(pdf_reader.getNumPages()):
                        pdf_writer.addPage(pdf_reader.getPage(page))
                stream_to_write = io.BytesIO()
                pdf_writer.write(stream_to_write)

                pdf_content = stream_to_write.getvalue()
                for temporary_file in temporary_files:
                    try:
                        os.unlink(temporary_file)
                    except (OSError, IOError):
                        _logger.error(
                            'Error when trying to remove file %s'
                            % temporary_file)
                return pdf_content, 'pdf'
            else:
                report_pdf = super(IrActionsReport, self)._render_qweb_pdf(
                    res_ids, data)
                drawing_template = self._get_drawing_template(res_ids, data, drawing_report)
                return self.add_drawing(res_ids, report_pdf, drawing_template)
        else:
            return super(IrActionsReport, self)._render_qweb_pdf(res_ids, data)

    @api.model
    def add_drawing(self, res_id, original_report_pdf, drawing_template):
        model = self.model
        object = self.env[model].browse(res_id)

        if drawing_template:
            writer = PdfFileWriter()
            if not any(drawing.print_only_drawing for drawing in drawing_template):
                stream_original_report = io.BytesIO(original_report_pdf[0])
                reader_original_report = PdfFileReader(stream_original_report)
                for page in range(0, reader_original_report.getNumPages()):
                    writer.addPage(reader_original_report.getPage(page))

            for drawing in drawing_template:
                attachment = drawing.sudo().drawing_ids.print_drawing_pdf(drawing.datas, object)
                attachment_decoded = base64.b64decode(attachment)
                stream_attachment = io.BytesIO(
                    attachment_decoded)
                reader_attachment = PdfFileReader(
                    stream_attachment)

                for page in range(0, reader_attachment.getNumPages()):
                    writer.addPage(reader_attachment.getPage(page))

            stream_to_write = io.BytesIO()
            writer.write(stream_to_write)

            combined_pdf = stream_to_write.getvalue()
            return combined_pdf, 'pdf'
        else:
            return original_report_pdf
