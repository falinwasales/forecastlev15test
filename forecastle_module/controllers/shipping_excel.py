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
class SaleExcelReportShipping(http.Controller):
    @http.route([
        '/sale/shipping_instruction/<model("sale.order"):sale_order>',
    ], type='http', auth="user", csrf=False)
    def get_shipping_report(self,sale_order=None,**args):
 
        response = request.make_response(
                    None,
                    headers=[
                        ('Content-Type', 'application/vnd.ms-excel'),
                        ('Content-Disposition', content_disposition('Shipping Instruction' + '.xlsx'))
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
            image_logo = BytesIO(base64.b64decode(sale.company_id.logo))
            # ************************************************



            #### ******************** FONT STYLE,ETC ****************************

            # !!!!!!!!!!!!!!!! FONT FOR HEADER !!!!!!!!!!!!!!!!
            header_font = workbook.add_format({'font_name': 'Times', 'font_size': 10, 'align': 'vcenter'})
            header_border_bottom= workbook.add_format({'bottom': 1, 'border_color': 'black'})
            # !!!!!!!!!!!!!!!! FONT FOR HEADER !!!!!!!!!!!!!!!!

            # !!!!!!!!!!!!!!!! FONT FOR UPPER TITLE !!!!!!!!!!!!!!!!
            upper_font_title = workbook.add_format({'font_name': 'Times', 'font_size': 13, 'align': 'vcenter', 'bold': True})
            # !!!!!!!!!!!!!!!! FONT FOR UPPER TITLE !!!!!!!!!!!!!!!!

            # !!!!!!!!!!!!!!!! FONT FOR UPPER STRATUM !!!!!!!!!!!!!!!!
            upper_stratum_static = workbook.add_format({'font_name': 'Times', 'font_size': 10, 'align': 'vcenter', 'bold': True})
            upper_stratum_font = workbook.add_format({'font_name': 'Times', 'font_size': 10, 'align': 'vcenter'})
            # !!!!!!!!!!!!!!!! FONT FOR UPPER STRATUM !!!!!!!!!!!!!!!!

            # !!!!!!!!!!!!!!!! FONT FOR MID STRATUM !!!!!!!!!!!!!!!!
            mid_stratum_th = workbook.add_format({
                'font_name': 'Times', 'font_size': 10, 'valign': 'vcenter', 
                'bold': True, 'border': 1, 'border_color': 'black','text_wrap': True,
                'align': 'center'})

            mid_stratum_td = workbook.add_format({
                'font_name': 'Times', 'font_size': 10, 'valign': 'vcenter', 
                'border': 1, 'border_color': 'black', 'text_wrap': True,
                'align': 'center'})
            # !!!!!!!!!!!!!!!! FONT FOR MID STRATUM !!!!!!!!!!!!!!!!

            # !!!!!!!!!!!!!!!! FONT FOR LOWER STRATUM !!!!!!!!!!!!!!!!
            lower_stratum_th = workbook.add_format({
                'font_name': 'Times', 'font_size': 10, 'valign': 'vcenter', 
                'bold': True, 'border': 1, 'border_color': 'black','text_wrap': True,
                'align': 'center'})

            lower_stratum_td = workbook.add_format({
                'font_name': 'Times', 'font_size': 10, 'valign': 'vcenter', 
                'border': 1, 'border_color': 'black', 'text_wrap': True,
                'align': 'center'})

            lower_stratum_total = workbook.add_format({
                'font_name': 'Times', 'font_size': 10, 'valign': 'vcenter', 
                'text_wrap': True, 'align': 'left'})

            lower_stratum_package = workbook.add_format({
                'font_name': 'Times', 'font_size': 10, 'valign': 'vcenter', 
                'text_wrap': True})
            # !!!!!!!!!!!!!!!! FONT FOR LOWER STRATUM !!!!!!!!!!!!!!!!

            #### ******************** FONT STYLE,ETC ****************************

            
            # y,x
            # ***************************** HEADER *****************************
            company_name = ''
            company_street = ''

            for record in sale.company_id:
                if record:
                    company_name = record.name
                    company_street = record.street

            sheet.insert_image(1, 0, 'Name' or '', {'image_data': image_logo, 'x_scale': 75/100, 'y_scale': 69.6/100})
            sheet.write(2, 0, company_name, header_font)
            sheet.write(3, 0, company_street, header_font)
            sheet.merge_range('A5:K5', '', header_border_bottom)
            # ***************************** HEADER *****************************

            # ***************************** UPPER TITLE *****************************
            sheet.merge_range('G7:I7', 'SHIPPING INSTRUCTION', upper_font_title)
            # ***************************** UPPER TITLE *****************************

            # ***************************** UPPER STRATUM LEFT(SHIPPER)*****************************
            principal_name = ''
            principal_street = ''
            principal_country = ''
            principal_phone = '-'

            for record in sale.principal_id:
                if record:
                    principal_name = record.name
                    principal_street = record.street
                    principal_country = record.country_id.name
                    principal_phone = record.phone

            sheet.write(8, 0, 'Shipper:', upper_stratum_static)
            sheet.write(9, 0, company_name, upper_stratum_static)
            sheet.write(10, 0, 'QQ.' +  principal_name, upper_stratum_font)
            sheet.write(11, 0, principal_street + '' + principal_country, upper_stratum_font)
            sheet.write(12, 0, 'Phone: %s' % (principal_phone), upper_stratum_font)
            # ***************************** UPPER STRATUM LEFT(SHIPPER)*****************************
            

            # ***************************** UPPER STRATUM LEFT(CONSIGEE)*****************************
            consignee_name = ''
            consignee_street = ''
            consignee_phone = '-'
            for record in sale.consignee_id:
                if record:
                    consignee_name = record.name
                    consignee_street = record.street
                    consignee_phone = record.phone
            sheet.write(14, 0, 'Consignee:', upper_stratum_static)
            sheet.write(15, 0, consignee_name, upper_stratum_font)
            sheet.write(16, 0, consignee_street, upper_stratum_font)
            sheet.write(17, 0, 'Phone: %s' % (consignee_phone), upper_stratum_font)
            # ***************************** UPPER STRATUM LEFT(SHIPPER)*****************************

            # ***************************** UPPER STRATUM LEFT(Notify Party)*****************************
            upper_stratum_row = 20

            notify_name = ''
            notify_address = ''
            notify_phone = '-'
            for x in sale.notify_id:
                if x:
                    notify_name = x.name
                    notify_address = x.street
                    notify_phone = x.phone

            for record in sale:
                sheet.write(19, 0, 'Notify Party:', upper_stratum_static)
                sheet.write(upper_stratum_row, 0, '', upper_stratum_font)
                if record.consignee_id:
                    if record.notify_id == record.consignee_id:
                        sheet.write(upper_stratum_row, 0, ('same as consignee').upper(), upper_stratum_font)
                    else:
                        sheet.write(upper_stratum_row, 0, notify_name, upper_stratum_font)
                        sheet.write(upper_stratum_row+1, 0, notify_address, upper_stratum_font)
                        sheet.write(upper_stratum_row+2, 0, 'Phone: %s' % (notify_phone), upper_stratum_font)
            # ***************************** UPPER STRATUM LEFT(Notify Party)*****************************


            # ***************************** UPPER STRATUM RIGHT(Contact Info)*****************************
            carrier_name = ''
            if sale.fal_carrier_id:
                for x in sale.fal_carrier_id:
                    carrier_name = x.name
            sheet.write(8, 6, 'To', upper_stratum_font)
            sheet.write(8, 7, ': %s' % (carrier_name), upper_stratum_font)
            # 
            feeder_name = ''
            feeder_phone = '-'
            feeder_mail = ''
            if sale.fal_feeder_pic:
                for x in sale.fal_feeder_pic:
                    feeder_name = x.name
                    feeder_phone = x.phone
                    feeder_mail = x.email
            sheet.write(9, 6, 'Attention', upper_stratum_font)
            sheet.write(9, 7, ': %s' % (feeder_name), upper_stratum_font)
            sheet.write(10, 6, 'Telp', upper_stratum_font)
            sheet.write(10, 7, ': %s' % (feeder_phone), upper_stratum_font)
            sheet.write(10, 6, 'Email', upper_stratum_font)
            sheet.write(10, 7, ': %s' % (feeder_mail), upper_stratum_font)
            # 
            bl_issue = ''
            freight = ''
            term = ''
            container = ''
            if sale:
                bl_issue = sale.bl_issue
                freight = sale.freight
                term = sale.term
                container = sale.fal_container_type

            sheet.write(11, 6, 'BL Issue', upper_stratum_font)
            sheet.write(11, 7, ': %s' % (bl_issue).capitalize(), upper_stratum_font)
            sheet.write(12, 6, 'Freight', upper_stratum_font)
            sheet.write(12, 7, ': %s' % (freight).capitalize(), upper_stratum_font)
            sheet.write(13, 6, 'Term', upper_stratum_font)
            sheet.write(13, 7, ': %s' % (term), upper_stratum_font)
            sheet.write(14, 6, 'Container', upper_stratum_font)
            sheet.write(14, 7, ': %s' % (container), upper_stratum_font)
            # 
            current_date = date.today().strftime('%d %b %Y')
            sheet.write(15, 6, 'Date', upper_stratum_font)
            sheet.write(15, 7, ': %s' % (current_date), upper_stratum_font)
            # 
            sheet.write(16, 6, 'Booking No', upper_stratum_font)
            sheet.write(16, 7, ': ' + sale.name or '', upper_stratum_font)
            # ***************************** UPPER STRATUM RIGHT(Contact Info)*****************************


             # ***************************** Mid STRATUM Table(TableHead)*****************************
            mid_stratum_th_row = upper_stratum_row + 4
            mid_stratum_th_col = 0

            sheet.write(mid_stratum_th_row, mid_stratum_th_col, 'Vessel', mid_stratum_th)
            sheet.write(mid_stratum_th_row, mid_stratum_th_col+1, 'Voyage', mid_stratum_th)
            sheet.write(mid_stratum_th_row, mid_stratum_th_col+2, 'POL', mid_stratum_th)
            sheet.write(mid_stratum_th_row, mid_stratum_th_col+3, 'ETD', mid_stratum_th)
            sheet.write(mid_stratum_th_row, mid_stratum_th_col+4, 'POD', mid_stratum_th)
            sheet.write(mid_stratum_th_row, mid_stratum_th_col+5, 'ETA', mid_stratum_th)
            sheet.write(mid_stratum_th_row, mid_stratum_th_col+6, 'Place of Receipt', mid_stratum_th)
            sheet.write(mid_stratum_th_row, mid_stratum_th_col+7, 'Final Destination', mid_stratum_th)
            sheet.write(mid_stratum_th_row, mid_stratum_th_col+8, 'ETA', mid_stratum_th)
            # ***************************** Mid STRATUM Table(TableHead)*****************************


            # ***************************** Mid STRATUM Table(TableData)*****************************
            mid_stratum_td_row = mid_stratum_th_row + 1
            mid_stratum_td_col = mid_stratum_th_col

            sheet.write(mid_stratum_td_row, mid_stratum_td_col, sale.re_vessel_id.name or '', mid_stratum_td)
            sheet.write(mid_stratum_td_row, mid_stratum_td_col + 1, sale.voyage_id.name or '', mid_stratum_td)
            sheet.write(mid_stratum_td_row, mid_stratum_td_col + 2, sale.pol_id.name or '', mid_stratum_td)
            sheet.write(mid_stratum_td_row, mid_stratum_td_col + 3, sale.etd.strftime('%d %b %Y'), mid_stratum_td)

            sheet.write(mid_stratum_td_row, mid_stratum_td_col + 4, '-', mid_stratum_td)
            sheet.write(mid_stratum_td_row, mid_stratum_td_col + 5, '-', mid_stratum_td)
            for record in sale.connecting_vessel_id:
                if sale.connecting_vessel_id:
                    sheet.write(mid_stratum_td_row, mid_stratum_td_col + 4, record[0].port_code_id.name, mid_stratum_td)
                    sheet.write(mid_stratum_td_row, mid_stratum_td_col + 5, record[0].date_eta.strftime('%d %b %Y'), mid_stratum_td)

            sheet.write(mid_stratum_td_row, mid_stratum_td_col + 6, sale.pol_id.port_full_name or '', mid_stratum_td)
            sheet.write(mid_stratum_td_row, mid_stratum_td_col + 7, sale.pod_id.name or '', mid_stratum_td)
            sheet.write(mid_stratum_td_row, mid_stratum_td_col + 8, sale.eta.strftime('%d %b %Y'), mid_stratum_td)
            # ***************************** Mid STRATUM Table(TableData)*****************************


            # ***************************** Lower STRATUM Table(TableHead)*****************************
            lower_stratum_th_row = mid_stratum_td_row + 3
            lower_stratum_th_col = mid_stratum_th_col

            sheet.merge_range('A%s:D%s' % (lower_stratum_th_row, lower_stratum_th_row), ('marks & number').upper(), lower_stratum_th)
            sheet.write(lower_stratum_th_row, lower_stratum_th_col, ('container').upper(), lower_stratum_th)
            sheet.write(lower_stratum_th_row, lower_stratum_th_col + 1, ('seal').upper(), lower_stratum_th)
            sheet.write(lower_stratum_th_row, lower_stratum_th_col + 2, ('size').upper(), lower_stratum_th)
            sheet.write(lower_stratum_th_row, lower_stratum_th_col + 3, ('type').upper(), lower_stratum_th)

            sheet.merge_range('E%s:E%s' % (lower_stratum_th_row, lower_stratum_th_row + 1), ('commodity').upper(), lower_stratum_th)

            sheet.write(lower_stratum_th_row - 1, lower_stratum_th_col + 5, ('net weight').upper(), lower_stratum_th)
            sheet.write(lower_stratum_th_row, lower_stratum_th_col + 5, ('kgs').upper(), lower_stratum_th)

            sheet.write(lower_stratum_th_row - 1, lower_stratum_th_col + 6, ('gross weight').upper(), lower_stratum_th)
            sheet.write(lower_stratum_th_row, lower_stratum_th_col + 6, ('kgs').upper(), lower_stratum_th)

            sheet.write(lower_stratum_th_row - 1, lower_stratum_th_col + 7, ('meas').upper(), lower_stratum_th)
            sheet.write(lower_stratum_th_row, lower_stratum_th_col + 7, ('m3').upper(), lower_stratum_th)

            sheet.write(lower_stratum_th_row - 1, lower_stratum_th_col + 8, ('hs').upper(), lower_stratum_th)
            sheet.write(lower_stratum_th_row, lower_stratum_th_col + 8, ('code').upper(), lower_stratum_th)

            sheet.merge_range('J%s:K%s' % (lower_stratum_th_row, lower_stratum_th_row + 1), ('description of packages and goods').upper(), lower_stratum_th)
            # ***************************** Lower STRATUM Table(TableHead)*****************************



            # ***************************** Lower STRATUM Table(TableData)*****************************
            lower_stratum_td_row = lower_stratum_th_row + 1
            lower_stratum_td_col = lower_stratum_th_col

            seal = 'TBA'
            gross = ''
            net = ''
            total_gross = ''
            for record in sale.cro_ids:
                if record:
                    seal = record.seal_number.name
                    temp_gross = record.gross.replace(',', '')
                    temp_gross2 = temp_gross.replace('.', '')
                    temp_net = record.nett.replace(',', '')
                    temp_net2 = temp_net.replace('.', '')
                    gross = float(str(temp_gross2))
                    net = float(str(temp_net2))

                sheet.write(lower_stratum_td_row, lower_stratum_td_col, record.container_number_id.name or 'TBA', lower_stratum_td)
                sheet.write(lower_stratum_td_row, lower_stratum_td_col + 1, seal, lower_stratum_td)
                sheet.write(lower_stratum_td_row, lower_stratum_td_col + 2, record.container_type_id.container_size or 'TBA', lower_stratum_td)
                sheet.write(lower_stratum_td_row, lower_stratum_td_col + 3, str(record.container_type_id.container_type).upper() or '-', lower_stratum_td)
                sheet.write(lower_stratum_td_row, lower_stratum_td_col + 4, record.hs_code.commodity or '-', lower_stratum_td)
                sheet.write(lower_stratum_td_row, lower_stratum_td_col + 5, net or 0, lower_stratum_td)
                sheet.write(lower_stratum_td_row, lower_stratum_td_col + 6, gross or 0, lower_stratum_td)
                sheet.write(lower_stratum_td_row, lower_stratum_td_col + 7, record.measure or 0, lower_stratum_td)
                sheet.write(lower_stratum_td_row, lower_stratum_td_col + 8, record.hs_code.digit_categories or 'TBA', lower_stratum_td)

                lower_stratum_td_row += 1
            
            sheet.write(lower_stratum_td_row + 10, lower_stratum_td_col + 4, 'TOTAL', lower_stratum_total)
            sheet.write_formula(lower_stratum_td_row + 10, lower_stratum_td_col + 5, "=SUM(F" + str(lower_stratum_th_row + 2) + ':F' + str(lower_stratum_td_row) + ")", lower_stratum_total)
            # sheet.write_formula(lower_stratum_td_row + 10, lower_stratum_td_col + 5, total_gross, lower_stratum_total)
            sheet.write_formula(lower_stratum_td_row + 10, lower_stratum_td_col + 6, "=SUM(G" + str(lower_stratum_th_row + 2) + ':G' + str(lower_stratum_td_row) + ")", lower_stratum_total)
            # ***************************** Lower STRATUM Table(TableData)*****************************


             # ***************************** Lower STRATUM Table(PackagesGood)*****************************
            lower_stratum_package_row = lower_stratum_th_row

            sheet.merge_range('J%s:K%s' % (lower_stratum_package_row + 2, lower_stratum_package_row + 3), ("shipper's stowed, load and count: ").upper(), lower_stratum_package)
            
            for record in sale.order_line.filtered(lambda x: x.product_id.is_container):
                uom = '-'
                size = '-'
                type = '-'
                desc = '-'
                if record:
                    uom = record.product_uom_qty
                    size = record.product_id.container_size
                    type = record.product_id.container_type
                    desc = sale.good_description
                    
                sheet.merge_range('J%s:K%s' % (lower_stratum_package_row + 4, lower_stratum_package_row + 4), 
                "%s x %s%s CONTAINER:" % (math.trunc(uom), size, type.upper()), lower_stratum_package)

                sheet.merge_range('J%s:K%s' % (lower_stratum_package_row + 5, lower_stratum_package_row + 5), 
                desc.upper(), lower_stratum_package)

            for x in sale.cro_ids.filtered(lambda x: x.imdg_class):
                imdg_class = '-'
                if x:
                    imdg_class = x[0].imdg_class
                sheet.merge_range('J%s:K%s' % (lower_stratum_package_row + 7, lower_stratum_package_row + 7), 
                ("imdg class :").upper() + imdg_class, lower_stratum_package)

            for x in sale.cro_ids.filtered(lambda x: x.un_number):
                un_number = '-'
                if x:
                    un_number = x[0].un_number
                sheet.merge_range('J%s:K%s' % (lower_stratum_package_row + 8, lower_stratum_package_row + 8), 
                ("un number :").upper() + un_number, lower_stratum_package)

            for x in sale.cro_ids.filtered(lambda x: x.pg_class):
                pg_class = '-'
                if x:
                    pg_class = x[0].pg_class
                sheet.merge_range('J%s:K%s' % (lower_stratum_package_row + 9, lower_stratum_package_row + 9), 
                ("pg class :").upper() + pg_class, lower_stratum_package)

            for x in sale.cro_ids.filtered(lambda x: x.ems_number):
                ems_number = '-'
                if x:
                    ems_number = x[0].ems_number
                sheet.merge_range('J%s:K%s' % (lower_stratum_package_row + 10, lower_stratum_package_row + 10), 
                ("ems number :").upper() + ems_number, lower_stratum_package)

            peb = "-"
            if sale.peb_no:
                peb = sale.peb_no
                sheet.merge_range('J%s:K%s' % (lower_stratum_package_row + 12, lower_stratum_package_row + 12), ("peb no: ").upper() + peb, lower_stratum_package)

            kpbc = "-"
            if sale.kpbc_code_id:
                kpbc = sale.kpbc_code_id.kpbc_code
                sheet.merge_range('J%s:K%s' % (lower_stratum_package_row + 13, lower_stratum_package_row + 13), ("kpbc: ").upper() + kpbc, lower_stratum_package)
            # ***************************** Lower STRATUM Table(PackagesGood)*****************************


           
            
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
 
        return response

            

# 
# 
# 