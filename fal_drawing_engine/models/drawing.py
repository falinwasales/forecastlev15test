
#-*- coding:utf-8 -*-
import base64
import io
from odoo import models, fields, api, tools, _
from odoo.tools.safe_eval import safe_eval
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode import code39
from reportlab.graphics.barcode import code128
from reportlab.lib.units import mm
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from reportlab.graphics.barcode import createBarcodeDrawing
from ast import literal_eval


import logging
_logger = logging.getLogger(__name__)


class FalDrawingTemplate(models.Model):
    _name = "fal.drawing.template"
    _description = "Drawing Template"

    name = fields.Char()
    preview = fields.Binary(string="PDF Preview", readonly=True)
    datas = fields.Binary(string="Attachment")
    print_only_drawing = fields.Boolean(string="Print Only Drawing", help="When you print a report it will only print the drawing")
    drawing_ids = fields.One2many('fal.drawing', 'template_id', string="Drawing Items", required=True, copy=True)
    drawing_report_ids = fields.One2many('fal.drawing.report', 'drawing_template_id', string="Reports")

    def pdf_preview(self):
        for draw in self:
            report = draw.drawing_report_ids and draw.drawing_report_ids[0]
            res_ids = False
            if report:
                res_ids = self.env[report.report_id.model].search(literal_eval(report.domain), limit=1)
            draw.preview = draw.drawing_ids.print_drawing_pdf(draw.datas, res_ids or draw)


class FalDrawing(models.Model):
    _name = "fal.drawing"
    _description = "Drawing"

    name = fields.Char(related="template_id.name", store=True)
    template_id = fields.Many2one('fal.drawing.template', string='Drawing Template')
    page_number = fields.Integer(string="Page Number", default=1, required=True)
    value = fields.Char(default="New")
    use_python_code = fields.Boolean(string="Use Python Code")
    python_code = fields.Text(
        string="Python Code",
        default='''
# res_id (to get active id)
# Example:
# value = res_id.field_name
value = "python value"
    ''')
    font_size = fields.Integer(string="Font Size", default=12)
    font_color = fields.Char(string="Font Color", default="#000000")
    rotation = fields.Selection([
        ("90", "90"),
        ("180", "180"),
        ("270", "270"),
    ], string="Rotate")
    posX = fields.Float(digits=(4, 3), string="Position X", required=True)
    posY = fields.Float(digits=(4, 3), string="Position Y", required=True)
    width = fields.Float(digits=(4, 3), string="Width Barcode", default=0.5)
    height = fields.Float(digits=(4, 3), string="Height Barcode", default=20.0)
    type_value = fields.Selection(
        [
            ('text', 'Text'),
            ('barcode', 'Barcode'), ],
        string='Type', default='text', required=True
    )

    def _compute_value(self, localdict):
        try:
            safe_eval(self.python_code, localdict, mode='exec', nocopy=True)
            return localdict['value']
        except Exception as e:
            return 'Wrong Input/python code'

    def print_drawing_pdf(self, datas, res_id):
        # datas: pdf file(attachment)
        # res_id: active_id (need to sent id. when call this function)
        if datas:
            old_pdf = False
            try:
                old_pdf = PdfFileReader(io.BytesIO(base64.b64decode(datas)), strict=False, overwriteWarnings=False)
            except Exception as e:
                raise UserError(_("This file cannot be read. Is it a valid PDF?"))

            packet = io.BytesIO()

            can = canvas.Canvas(packet)
            # c = canvas.Canvas("barcode_example.pdf",pagesize=A4)
            page_number = 0
            for p in range(0, old_pdf.getNumPages()):
                page_number += 1
                page = old_pdf.getPage(p)
                width = float(page.mediaBox.getUpperRight_x())
                height = float(page.mediaBox.getUpperRight_y())

                for item in self:
                    if item.page_number == page_number:
                        # Set page orientation (either 0, 90, 180 or 270)
                        posY, posX = item.posY, item.posX
                        rotation = item.rotation and int(item.rotation)
                        if rotation:
                            can.saveState()
                            can.rotate(rotation)
                            if rotation == 90:
                                posY = -posX
                                posX = item.posY
                            elif rotation == 180:
                                posX = -posX
                                posY = -posY
                            elif rotation == 270:
                                posX = -posY
                                posY = item.posX

                        font = "Helvetica"
                        normalFontSize = item.font_size or 12
                        can.setFont(font, normalFontSize)
                        value = item.value

                        localdict = {
                        **{
                                'res_id': res_id,
                                'value': '',
                            }
                        }
                        if item.use_python_code:
                            value = item._compute_value(localdict)

                        if item.font_color:
                            can.setFillColor(item.font_color)

                        textobject = can.beginText()
                        textobject.setTextOrigin(posX, posY)
                        if value:
                            value = value.split('\n')
                        else:
                            value = ''
                        for v in value:
                            textobject.textLine(text=v)

                        # check type value is a barcode or text
                        if item.type_value == 'barcode':
                            # generate barcode
                            barcode = code128.Code128(value[0],barWidth=item.width*mm,barHeight=item.height*mm)
                            barcode.drawOn(can, posX, posY)
                        else:
                            can.drawText(textobject)

                        if rotation:
                            can.restoreState()

                can.showPage()
            can.save()


            item_pdf = PdfFileReader(packet, overwriteWarnings=False)
            new_pdf = PdfFileWriter()

            for p in range(0, old_pdf.getNumPages()):
                page = old_pdf.getPage(p)
                page.mergePage(item_pdf.getPage(p))
                new_pdf.addPage(page)

            output = io.BytesIO()
            new_pdf.write(output)
            # output.close()
            return base64.b64encode(output.getvalue())


class FalDrawingReport(models.Model):
    _name = "fal.drawing.report"
    _description = "Drawing"

    report_id = fields.Many2one('ir.actions.report', string="Reports", domain=[('report_type', '=', 'qweb-pdf')])
    drawing_template_id = fields.Many2one('fal.drawing.template', string='Drawing Template')
    domain = fields.Char(default='[]')
    model = fields.Char(related="report_id.model")
