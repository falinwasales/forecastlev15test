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
import logging
import math

_logger = logging.getLogger(__name__)
class PreAlertExcel(http.Controller):
    @http.route([
        '/sale/pre_alert/<model("sale.order"):sale_order>',
    ], type='http', auth="user", csrf=False)
    def get_pre_alert_report(self,sale_order=None,**args):
 
        response = request.make_response(
                    None,
                    headers=[
                        ('Content-Type', 'application/vnd.ms-excel'),
                        ('Content-Disposition', content_disposition('pre alert' + '.xlsx'))
                    ]
                )
 
        # buat object workbook dari library xlsxwriter
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        # workbook.set_paper(9)
 
 
        # loop user / sales person yang dipilih
        for sale in sale_order:
            sheet = workbook.add_worksheet(sale.name)
            # sheet.set_landscape()
            sheet.set_paper(9)
            sheet.set_margins(0.5,0.5,0.5,0.5)
 
            sheet.set_column('A:Z', 14)


            # ******************** IMAGE BINARY ****************************
            company = BytesIO(base64.b64decode(sale.company_id.logo)) # to convert it to base64 file

            principal = BytesIO(base64.b64decode(sale.principal_id.image_1920)) # to convert it to base64 file
            # ************************************************


            #### ******************** FONT STYLE,ETC ****************************

            # ********************* UPPER-LEFT STRATUM *****************
            upper_left_stratum_header = workbook.add_format({'font_name': 'Times', 'font_size': 15, 'align': 'vcenter'})
            upper_left_stratum_static = workbook.add_format({'font_name': 'Times', 'font_size': 10, 'align': 'vcenter', 'bold': True})
            upper_stratum_font = workbook.add_format({'font_name': 'Times', 'font_size': 10, 'align': 'vcenter'})
            # ********************* UPPER-LEFT STRATUM *****************

            # ********************* MIDDLE STRATUM *****************
            middle_stratum_static = workbook.add_format({'font_name': 'Times', 'font_size': 10, 'align': 'vcenter', 
            'align' : 'center', 'bold': True, 'border': 1, 'border_color': 'black',})
            middle_stratum_font = workbook.add_format({'font_name': 'Times', 'font_size': 10, 'align': 'vcenter', 
            'align' : 'center', 'bold': False, 'border': 1, 'border_color': 'black',})
            # ********************* MIDDLE STRATUM *****************

            # ********************* LOWER STRATUM *****************
            lower_stratum_static = workbook.add_format({'font_name': 'Times', 'font_size': 12, 'align': 'vcenter', 
            'align' : 'center', 'bold': True, 'border': 1, 'border_color': 'black',})
            # ********************* LOWER STRATUM *****************


            #### ******************** FONT STYLE,ETC ****************************


            #### ******************** UPPER-LEFT STRATUM ****************************
            to = ''
            street = ''
            city = ''
            state = ''
            country = ''
            email = '-'
            for record in sale.principal_id:
                if record:
                    to = record.name
                    street = record.street
                    city = record.city
                    country = record.country_id.name
                    state = record.state_id.name
                    email = record.email

            vessel = ''
            if sale.re_vessel_id:
                vessel = sale.re_vessel_id.name
            
            voyage = ''
            if sale.voyage_id:
                voyage = sale.voyage_id.name

            atd = ''
            if sale.date_td:
                atd = sale.date_td.strftime('%d %b %Y')

            eta = ''
            if sale.eta:
                eta = sale.eta.strftime('%d %b %Y')

            sheet.merge_range('A1:D1', ('pre alert report').upper(), upper_left_stratum_header)
            sheet.merge_range('A3:B3', ('to').capitalize(), upper_left_stratum_static)
            sheet.merge_range('A4:B5', ('address').capitalize(), upper_left_stratum_static)
            sheet.merge_range('A6:B6', ('email').capitalize(), upper_left_stratum_static)
            sheet.merge_range('A7:B7', ('vessel').capitalize(), upper_left_stratum_static)
            sheet.merge_range('A8:B8', ('voyage').capitalize(), upper_left_stratum_static)
            sheet.merge_range('A9:B9', ('atd pol').upper(), upper_left_stratum_static)
            sheet.merge_range('A10:B10', ('eta thlch').upper(), upper_left_stratum_static)

            #(((((((((((((((((((FIELD))))))))))))))))#
            sheet.write(2,2, ': ' + to.upper(), upper_left_stratum_static)
            sheet.write(3,2, ': ' + street, upper_stratum_font)
            sheet.write(4,2, ' ' + city + ',' + country, upper_stratum_font)
            sheet.write(5,2, ': %s' % (email), upper_stratum_font)
            sheet.write(6,2, ': ' + vessel, upper_stratum_font)
            sheet.write(7,2, ': ' + voyage, upper_stratum_font)
            sheet.write(8,2, ': ' + str(atd), upper_stratum_font)
            sheet.write(9,2, ': ' + str(eta), upper_stratum_font)
            #### ******************** UPPER-LEFT STRATUM ****************************

            
            #### ******************** UPPER-RIGHT STRATUM ****************************
            sheet.insert_image(1, 7, 'Name', {'image_data': principal, 'x_scale': 252/100, 'y_scale': 197/100})
            #### ******************** UPPER-RIGHT STRATUM ****************************

            
            #### ******************** MIDDLE STRATUM(TableHead) ****************************
            sheet.write(12,0, 'bill of lading'.capitalize(), middle_stratum_static)
            sheet.write(13,0, 'number'.capitalize(), middle_stratum_static)
            sheet.write(12,1, 'container'.capitalize(), middle_stratum_static)
            sheet.write(13,1, 'number'.capitalize(), middle_stratum_static)
            sheet.write(12,2, 'seal'.capitalize(), middle_stratum_static)
            sheet.write(13,2, 'number'.capitalize(), middle_stratum_static)
            sheet.merge_range('D13:D14', ('size').capitalize(), middle_stratum_static)
            sheet.merge_range('E13:E14', ('type').capitalize(), middle_stratum_static)
            sheet.write(12,5, 'gross weight'.capitalize(), middle_stratum_static)
            sheet.write(13,5, 'kgs'.upper(), middle_stratum_static)
            sheet.write(12,6, 'tare weight'.capitalize(), middle_stratum_static)
            sheet.write(13,6, 'kgs'.upper(), middle_stratum_static)
            sheet.write(12,7, 'vgm'.upper(), middle_stratum_static)
            sheet.write(13,7, 'kgs'.upper(), middle_stratum_static)
            sheet.write(12,8, 'port of'.capitalize(), middle_stratum_static)
            sheet.write(13,8, 'discharge'.capitalize(), middle_stratum_static)
            sheet.write(12,9, 'final'.capitalize(), middle_stratum_static)
            sheet.write(13,9, 'destination'.capitalize(), middle_stratum_static)
            sheet.merge_range('K13:K14', ('hs code').capitalize(), middle_stratum_static)
            sheet.merge_range('L13:N13', ('MV connection details').capitalize(), middle_stratum_static)
            sheet.write(13,11, 'vessel'.capitalize(), middle_stratum_static)
            sheet.write(13,12, 'voyage'.capitalize(), middle_stratum_static)
            sheet.write(13,13, 'eta pot'.upper(), middle_stratum_static)
            sheet.write(12,14, 'slot'.upper(), middle_stratum_static)
            sheet.write(13,14, 'owner'.upper(), middle_stratum_static)
            #### ******************** MIDDLE STRATUM(TableHead) ****************************


            #### ******************** MIDDLE STRATUM(TableData) ****************************
            middle_stratum_data_row = 14

            container_number = '-'
            seal = ''
            container_size = ''
            container_type = ''
            tare = 0
            gross = ''
            measure = 0
            voyage_name = ''
            pod = ''
            bl_number = ''
            hs_code = ''
            connecting_vessel_name = ''
            date_eta = ''
            port_code = ''
            carrier = ''

            for record in sale.cro_ids:
                container_number = record.container_number_id.name
                seal = record.seal_number.name
                container_size = record.container_type_id.container_size
                container_type = record.container_type_id.container_type

                for x in sale.picking_ids:
                    for z in x.move_line_ids_without_package.filtered(lambda x: x.lot_id == record.container_number_id):
                        tare = z.tare

                temp_gross = record.gross.replace(',', '')
                temp_gross2 = temp_gross.replace('.', '')
                gross = float(str(temp_gross2))
                temp_meas = record.measure.replace(',', '')
                temp_meas2 = temp_meas.replace('.', '')
                measure = float(str(temp_meas2))
                voyage_name = sale.voyage_id.name
                pod = sale.pod_id.name
                bl_number = sale.bl_number
                hs_code = record.hs_code.name

                for line in sale.connecting_vessel_id:
                    connecting_vessel_name = line.vessel_id.name
                    date_eta = line.date_eta
                    port_code = line.port_code_id.name

                carrier = sale.fal_carrier_id.feeder_code

                sheet.write(middle_stratum_data_row,0, container_number, middle_stratum_font)
                sheet.write(middle_stratum_data_row,1, seal, middle_stratum_font)
                sheet.write(middle_stratum_data_row,2, container_size, middle_stratum_font)
                sheet.write(middle_stratum_data_row,3, container_type, middle_stratum_font)
                sheet.write(middle_stratum_data_row,4, tare, middle_stratum_font)
                sheet.write(middle_stratum_data_row,5, gross, middle_stratum_font)
                sheet.write(middle_stratum_data_row,6, measure, middle_stratum_font)
                sheet.write(middle_stratum_data_row,7, voyage_name, middle_stratum_font)
                sheet.write(middle_stratum_data_row,8, pod, middle_stratum_font)
                sheet.write(middle_stratum_data_row,9, bl_number, middle_stratum_font)
                sheet.write(middle_stratum_data_row,10, hs_code, middle_stratum_font)
                sheet.write(middle_stratum_data_row,11, connecting_vessel_name, middle_stratum_font)
                sheet.write(middle_stratum_data_row,12, date_eta, middle_stratum_font)
                sheet.write(middle_stratum_data_row,13, port_code, middle_stratum_font)
                sheet.write(middle_stratum_data_row,14, carrier, middle_stratum_font)

                middle_stratum_data_row += 1

            sheet.write('B' + str(middle_stratum_data_row + 2), ('total').upper(), middle_stratum_font)
            sheet.write_formula('F' + str(middle_stratum_data_row + 2), '=SUM(F15:F' + str(middle_stratum_data_row) + ')', middle_stratum_font)
            sheet.write_formula('G' + str(middle_stratum_data_row + 2), '=SUM(G15:G' + str(middle_stratum_data_row) + ')', middle_stratum_font)
            #### ******************** MIDDLE STRATUM(TableData) ****************************


            #### ******************** LOWER STRATUM ****************************
            lower_stratum_row = middle_stratum_data_row + 8

            company_name = ''
            company_street = ''
            company_city = ''
            company_phone = '-'
            company_email = '-'
            if sale.company_id:
                company_name = sale.company_id.name
                company_street = sale.company_id.street
                company_city = sale.company_id.city
                company_phone = sale.company_id.phone
                company_email = sale.company_id.email

            sheet.insert_image('A%s' % str(lower_stratum_row), 'test_logo',  {'image_data': company, 'x_scale': 80/100, 'y_scale': 100/100})
            sheet.write(lower_stratum_row + 2, 0, 'as agent', upper_left_stratum_static)
            sheet.merge_range('A%s:B%s' % (str(lower_stratum_row + 3), str(lower_stratum_row + 3)), company_name.upper(), lower_stratum_static)
            sheet.write(lower_stratum_row + 3, 0, company_street.capitalize() + str(company_city.capitalize()), upper_left_stratum_static)

            sheet.merge_range('A%s:B%s' % (str(lower_stratum_row + 5), str(lower_stratum_row + 5)), ('phone').capitalize(), upper_left_stratum_static)
            sheet.write(lower_stratum_row + 4, 2, ': ' + str(company_phone), upper_left_stratum_static)

            sheet.merge_range('A%s:B%s' % (str(lower_stratum_row + 6), str(lower_stratum_row + 6)), ('email').capitalize(), upper_left_stratum_static)
            sheet.write(lower_stratum_row + 5, 2, ': ' + str(company_email), upper_left_stratum_static)
            #### ******************** LOWER STRATUM ****************************
            
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
 
        return response

            

# 
# 
# 