# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
# from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression
import base64
from datetime import date
from collections import OrderedDict
import logging

_logger = logging.getLogger(__name__)


class CustomerPortal(CustomerPortal):

    @http.route(['/my/orders/<int:order_id>/schedule'], type='http', auth="public", methods=['POST'], website=True)
    def schedule(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        message = post.get('voyage_id', False)

        query_string = False
        order_sudo.write({'voyage_id': message})
        return request.redirect(order_sudo.get_portal_url(query_string=query_string))
    #######################################################################
    # COPY CONTAINER

    @http.route(['/my/orders/<int:order_id>/copycontainer'], type='http', auth="public", methods=['POST'], website=True)
    def copycontainer(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        message_container = post.get('container_id', False)
        message_apply_to_container = post.get('container_id_apply', False)
        cro_id = order_sudo.cro_ids.sudo().filtered(lambda x: x.id == int(message_apply_to_container))
        cro_id_asal = order_sudo.cro_ids.sudo().filtered(lambda x: x.id == int(message_container))
        if message_apply_to_container:
            cro_id.write({'commodity_type': cro_id_asal.commodity_type,
                            'container_categ': cro_id_asal.container_categ,
                            'gross': cro_id_asal.gross,
                            'nett': cro_id_asal.nett,
                            'measure': cro_id_asal.measure,
                            'imdg_class': cro_id_asal.imdg_class,
                            'ems_number': cro_id_asal.ems_number,
                            'un_number': cro_id_asal.un_number,
                            'pg_class': cro_id_asal.pg_class,
                            'set_temp': cro_id_asal.set_temp,
                            'length': cro_id_asal.length,
                            'height': cro_id_asal.height,
                            'width': cro_id_asal.width,
                            'total_outer_dimension': cro_id_asal.total_outer_dimension,
                            'hs_code': cro_id_asal.hs_code,
                            'seal_number': cro_id_asal.seal_number})
            # order_sudo.message_apply_to_container.write({''})

        query_string = False
        return request.redirect(order_sudo.get_portal_url(query_string=query_string))

    #######################################################################

    @http.route(['/my/orders/<int:order_id>/booking'], type='http', auth="public", methods=['POST'], website=True)
    def booking(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        query_string = False
        order_sudo._check_shipper()
        order_sudo._check_gross_weight_container()
        order_sudo.write({'booking': True})
        return request.redirect(order_sudo.get_portal_url(query_string=query_string))

    @http.route(['/my/orders/<int:order_id>/surendered'], type='http', auth="public", methods=['POST'], website=True)
    def surendered(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        query_string = False
        order_sudo.sudo().action_surender()
        order_sudo.write({'surendered': True})
        return request.redirect(order_sudo.get_portal_url(query_string=query_string))

    @http.route(['/my/orders/<int:order_id>/seawaybill'], type='http', auth="public", methods=['POST'], website=True)
    def seawaybill(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        query_string = False
        order_sudo.sudo().write({'seawaybill': True})
        return request.redirect(order_sudo.get_portal_url(query_string=query_string))

    @http.route(['/my/orders/<int:order_id>/final_si'], type='http', auth="public", methods=['POST'], website=True)
    def final_si(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        query_string = False
        order_sudo._check_consignee_notify()
        order_sudo._check_validate_delivery()
        order_sudo._check_peb()
        order_sudo._check_hs_code()
        order_sudo.write({'final_si': True})
        # Generate BL Number
        order_sudo.action_generate_bl_number()
        return request.redirect(order_sudo.get_portal_url(query_string=query_string))

    @http.route(['/my/orders/<int:order_id>/confirm_draft_bl'], type='http', auth="public", methods=['POST'], website=True)
    def confirm_draft_bl(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        query_string = False
        order_sudo.write({'confirmed_draft_bl': True})
        return request.redirect(order_sudo.get_portal_url(query_string=query_string))

    @http.route(['/my/orders/<int:order_id>/confirm'], type='http', auth="public", methods=['POST'], website=True)
    def confirm(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        query_string = False
        if order_sudo.is_import:
            order_sudo.write({'noa_confirmed': True})
            if order_sudo.operating_unit_id:
                journal_id = request.env['account.journal'].search([('type', 'in', ['sale']), ('operating_unit_id', '=', order_sudo.operating_unit_id.id)], limit=1)
                order_sudo.with_context(default_journal_id=journal_id.id)._auto_create_invoice_import()
            else:
                order_sudo._auto_create_invoice_import()
            order_sudo.write({'state': 'done'})
            order_sudo.message_post(body=_('Your shipment %s you can release SPDO') % (order_sudo.name), channel_ids=order_sudo.message_channel_ids.ids)
        else:
            order_sudo.write({'proforma_confirmed': True})
            # Search good invoice journal
            if order_sudo.operating_unit_id:
                journal_id = request.env['account.journal'].search([('type', 'in', ['sale']), ('operating_unit_id', '=', order_sudo.operating_unit_id.id)], limit=1)
                order_sudo.with_context(default_journal_id=journal_id.id)._auto_create_invoice()
            else:
                order_sudo._auto_create_invoice()
            order_sudo.write({'state': 'done'})
        # order_sudo.action_add_proforma_invoice()
        return request.redirect(order_sudo.get_portal_url(query_string=query_string))

    @http.route(['/my/orders/<int:order_id>/container'], type='http', auth="public", methods=['POST'], website=True)
    def container(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        message_sale_line_id = post.get('sale_line_id', False)
        message_container_quantity = post.get('Quantity', False)

        query_string = False
        sale_line_sudo = request.env['sale.order.line'].sudo().browse(int(message_sale_line_id))
        product_set_id = sale_line_sudo and sale_line_sudo.product_set_id and sale_line_sudo.product_set_id.id or False
        # Get the Set id of the sale line id
        if product_set_id and message_container_quantity:
            # 1. Remove all line related to this product set on this sale order
            order_sudo.order_line.sudo().filtered(lambda x: x.product_set_id.id == int(product_set_id)).unlink()
            # 2. Call add set method
            product_set_add = request.env['product.set.add'].sudo().create({
                'order_id': order_id,
                'product_set_id': product_set_id,
                'quantity': message_container_quantity,
            })
            product_set_add.add_set()
            order_sudo.create_cro_lines()

            # Add charges info
            order_sudo.create_charge_info()
        return request.redirect(order_sudo.get_portal_url(query_string=query_string))

    @http.route(['/my/orders/<int:order_id>/containerreleaseorder'], type='http', auth="public", methods=['POST'], website=True)
    def containcontainerreleaseorderer(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        message_cro_id = post.get('container_info_id', False)
        cro_id = order_sudo.cro_ids.sudo().filtered(lambda x: x.id == int(message_cro_id))
        message_cro_commodity_type = post.get('commodity_type', False) or cro_id.commodity_type
        message_cro_container_categ = post.get('container_categ', False) and post.get('container_categ', False).lower() or cro_id.container_categ

        message_cro_gross = post.get('gross', 0)
        message_cro_nett = post.get('nett', 0)
        message_cro_measure = post.get('measure', 0)
        if message_cro_commodity_type == 'Dangerous Good':
            message_cro_commodity_type = 'dg'
        elif message_cro_commodity_type == 'Standard':
            message_cro_commodity_type = 'standard'
        message_cro_imdg = post.get('imdg', 0)
        message_cro_ems = post.get('ems', 0)
        message_cro_un = post.get('un', 0)
        message_cro_pg_class = post.get('pg_class', 0)
        message_cro_temp = post.get('temp', 0)
        message_cro_seal = post.get('seal', 0)
        message_cro_lenth = post.get('lenth', 0)
        message_cro_height = post.get('height', 0)
        message_cro_width = post.get('width', 0)
        message_cro_dimension = post.get('dimension', 0)
        # Net and Gros
        if not message_cro_gross or not message_cro_nett:
            raise UserError(_('Gross or Nett Is Empty'))

        # Commodity
        message_commodity_ids = [int(post.get('commodity', 0)), int(post.get('commodity2', 0)), int(post.get('commodity3', 0)), int(post.get('commodity4', 0))]
        # Remove all value with 0 (Select...)
        message_commodity_ids = [i for i in message_commodity_ids if i != 0]
        # HS CODE
        hs_code = request.env['fce.hs.code']
        message_hs_ids = [post.get('hs', 0), post.get('hs2', 0), post.get('hs3', 0), post.get('hs4', 0), post.get('hs5', 0)]
        if message_hs_ids:
            hs = hs_code.sudo().search(['|', ('name', 'in', message_hs_ids), ('digit_categories', 'in', message_hs_ids)])
            message_hs_ids = hs.ids
            if order_sudo.internal_confirm and not hs:
                raise UserError(_('HS code that you input does not exist'))
        # Seal Number
        seal_number = False
        if message_cro_seal:
            seal_obj = request.env['fce.seal.number']
            seal_number = seal_obj.sudo().search([('name', '=', message_cro_seal)], limit=1)
            if not seal_number:
                seal_number = seal_obj.sudo().create({'name': message_cro_seal})
            else:
                if seal_number.cro_ids and seal_number.cro_ids[0] != cro_id:
                    raise UserError(_('Seal Number have been Used'))

        contno = int(post.get('contno', 0)) or False
        # Remove all value with 0 (Select...)
        message_hs_ids = [i for i in message_hs_ids if i != 0]
        # fix_gross = message_cro_gross.replace(',', '').replace('.', '')
        # fix_net = message_cro_nett.replace(',', '').replace('.', '')
        # fix_measure = message_cro_measure.replace(',', '').replace('.', '')

        query_string = False
        cro_id.sudo().write({'container_categ': message_cro_container_categ, 'container_number_id': contno, 'seal_number': seal_number, 'gross': message_cro_gross, 'nett': message_cro_nett, 'measure': message_cro_measure, 'commodity_type': message_cro_commodity_type, 'imdg_class': message_cro_imdg, 'ems_number': message_cro_ems, 'un_number': message_cro_un, 'pg_class': message_cro_pg_class, 'set_temp': message_cro_temp, 'length': message_cro_lenth, 'height': message_cro_height, 'width': message_cro_width, 'total_outer_dimension': message_cro_dimension, 'commodity': [(6, 0, message_commodity_ids)], 'hs_code': [(6, 0, message_hs_ids)]})
        return request.redirect(order_sudo.get_portal_url(query_string=query_string))

    @http.route(['/my/orders/<int:order_id>/charges'], type='http', auth="public", methods=['POST'], website=True)
    def charges(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        message_charge_id = post.get('charge_info_id', False)
        message_payment_term = post.get('fce_payment_term', False)
        message_bill_to_id = int(post.get('bill_to_id', False))
        if not message_bill_to_id:
            message_bill_to_id = False

        query_string = False
        charge_id = request.env['charge.info'].sudo().browse(int(message_charge_id))

        charge_id.sudo().write({'fce_payment_term': message_payment_term, 'bill_to_id': message_bill_to_id})

        return request.redirect(order_sudo.get_portal_url(query_string=query_string))

    @http.route(['/my/orders/<int:order_id>/contact'], type='http', auth="public", methods=['POST'], website=True)
    def contact(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        message_contact_selection = post.get('related_booking_party', False)
        message_contact_name = post.get('contact_name', False)
        message_contact_street = post.get('contact_street', False)
        if message_contact_selection == '':
            order_sudo.partner_id.write({
                    'fal_related_party_ids': [(0, 0, {
                        "name": message_contact_name,
                        "street": message_contact_street,
                        "is_consignee": True,
                        'is_notify': True,
                        "is_shipper": True,
                        "is_customer": True,
                        "supplier_rank": 1,
                        "customer_rank": 1})]
            })
        else:
            partner = request.env['res.partner'].sudo().search([('id', '=', message_contact_selection)])
            partner.sudo().write({'name': message_contact_name, 'street': message_contact_street})
        query_string = False
        return request.redirect(order_sudo.get_portal_url(query_string=query_string))

    @http.route(['/my/orders/<int:order_id>/bookshipment'], type='http', auth="public", methods=['POST'], website=True)
    def bookshipment(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        order_sudo.copy()
        query_string = False
        return request.redirect(order_sudo.get_portal_url(query_string=query_string))

    @http.route(['/my/orders/<int:order_id>/shipper'], type='http', auth="public", methods=['POST'], website=True)
    def shipper(self, order_id, access_token=None, **post):
        print('===================================================== SHIPPER =============================')
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        message_unit = post.get('unit', False)
        message_shiper = post.get('shipper_id', False)
        message_package_code_id = post.get('package_code_id', False)
        message_shipper_address = post.get('shipper_address', False)
        message_consignee_id = post.get('consignee_id', False)
        message_consignee_address = post.get('consignee_address', False)
        message_notify = post.get('notify_id', False)
        message_notify_address = post.get('notify_address', False)
        message_container_type = post.get('container_type', False)
        message_container_number = post.get('container_number', False)
        message_gross_weight = post.get('gross_weight', False)
        message_net_weight = post.get('net_weight', False)
        message_measure = post.get('measure', False)
        message_comodity = post.get('comodity', False)
        message_international_term = post.get('international_term', False)
        message_hs_code = post.get('hs_code', False)
        message_peb_no = post.get('peb_no', False)
        message_kppbc = post.get('kppbc', False)
        message_peb_date = post.get('peb_date', False)
        message_detention = post.get('detention', False)
        message_goods = post.get('goods', False)
        message_remarks = post.get('remarks', False)
        message_kpbc_code_id = post.get('kpbc_code_id', False)
        print('message_shiper================================')
        print(message_shiper)

        if message_shiper == '0':
            message_shiper = False
        if message_consignee_id == '0':
            message_consignee_id = False
        if message_notify == '0':
            message_notify = False
        if message_package_code_id == '0':
            message_package_code_id = True
        if message_kpbc_code_id == '0':
            message_kpbc_code_id = True

        query_string = False
        order_sudo.write({'shipper_id': message_shiper,
                          'shipper_address': message_shipper_address,
                          'consignee_id': message_consignee_id,
                          'consignee_address': message_consignee_address,
                          'notify_id': message_notify,
                          'notify_address': message_notify_address,
                          'package_code_id': message_package_code_id,
                          'container_type_id': message_container_type,
                          'container_no': message_container_number,
                          'gross_weight': message_gross_weight,
                          'net_weight': message_net_weight,
                          'measure': message_measure,
                          'commodity': message_comodity,
                          'international_term': message_international_term,
                          'hs_code': message_hs_code,
                          'peb_no': message_peb_no,
                          'unit': message_unit,
                          'peb_date': message_peb_date,
                          'kppbc': message_kppbc,
                          'kpbc_code_id': message_kpbc_code_id,
                          'detention': message_detention,
                          'good_description': message_goods,
                          'remarks': message_remarks})

        return request.redirect(order_sudo.get_portal_url(query_string=query_string))

    def _get_deposit_charges(self, order):
        data_det = []
        for x in order.import_container_info_ids:
            data_det.append([x.product_id, x.con_deposit, x.quantity])

        res_det = {}
        for prod, deposit, qty in data_det:
            if prod in res_det:
                res_det[prod]['prod'] = prod
                res_det[prod]['qty'] += qty
                res_det[prod]['deposit'] += deposit
            else:
                res_det[prod] = {'prod': prod, 'qty': qty, 'deposit': deposit}

        container_data_det = []
        for record in res_det:
            container_data_det.append(res_det[record])

        return container_data_det

    def _order_get_page_view_values(self, order, access_token, **kwargs):
        cro_ids = False
        hs_ids = False
        bill_to_ids = False
        detention_ids = order and order.import_container_info_ids
        deposit_charges = order and self._get_deposit_charges(order)
        repair_ids = request.env['stock.move.line']
        picking_ids = request.env['stock.picking'].browse(order._get_delivery_purchase())
        for picking in picking_ids:
            for line in picking.move_line_ids_without_package.filtered(lambda a: a.repair_status):
                repair_ids |= line

        if order and order.validity_date and order.pol_id and order.pod_id:
            voyage_ids = request.env['fce.voyage'].sudo().search([('date_etd', '<=', order.start_date), ('date_eta', '>=', order.validity_date), ('port_of_call_ids.port_code_id', '=', order.pol_id.id), ('port_of_call_ids.port_code_id', '=', order.pod_id.id)])

            filter_voyage = []
            for voyage in voyage_ids:
                for slot in voyage.slot_owner_ids:
                    if order.fal_carrier_id.id == slot.vendor_ids.id:
                        filter_voyage.append(voyage.id)
            voyage_ids = request.env['fce.voyage'].sudo().browse(filter_voyage)

            shipper_id = order.partner_id.fal_related_party_ids
            consignee_id = order.partner_id.fal_related_party_ids
            notify_id = order.partner_id.fal_related_party_ids
            bill_to_ids = order.partner_id.fal_related_party_ids + order.partner_id
            product_set = []
            if order.order_line.product_set_id:
                for p in order.order_line.product_set_id:
                    product_sets = request.env['product.set'].sudo().search([('id', '=', p.id)])
                    product_set.append(product_sets)
            cro_ids = order.cro_ids
            commodity_ids = request.env['fce.commodity'].sudo().search([])
            hs_ids = request.env['fce.hs.code'].sudo().search([])
            lot_ids = []
            for picking in order.picking_ids.filtered(lambda a: a.state != 'cancel'):
                for line in picking.move_line_ids_without_package:
                    if line.lot_id and (not any(line.lot_id.id == cro_id.container_number_id.id for cro_id in order.cro_ids.filtered(lambda x: x.container_number_id))):
                        lot_ids.append(line.lot_id.id)
        else:
            voyage_ids = []
            shipper_id = []
            consignee_id = []
            notify_id = []
            product_set = []
            commodity_ids = []
            lot_ids = []

        values = {
            'sale_order': order,
            'token': access_token,
            'return_url': '/shop/payment/validate',
            'voyage_ids': voyage_ids,
            'detention_ids': detention_ids,
            'repair_ids': repair_ids,
            'deposit_charges': deposit_charges,
            'shipper_id': shipper_id,
            'package_code_id': request.env['fce.package.code'].sudo().search([]),
            'kpbc_code_id': request.env['fce.kpbc.code'].sudo().search([]),
            'consignee_id': consignee_id,
            'notify_id': notify_id,
            'cro_ids': cro_ids,
            'commodity_ids': commodity_ids,
            'hs_ids': hs_ids,
            'lot_ids': request.env['stock.production.lot'].sudo().browse(lot_ids),
            'bill_to_ids': bill_to_ids,
            'product_sets': product_set,
            'partner_ids': request.env['res.partner'].sudo().search([]),
            'product_template': request.env['product.template'].sudo().search([]),
            'international_term': request.env['account.incoterms'].sudo().search([]),
            'hs_code': request.env['fce.hs.code'].sudo().search([]),
            'seal_number': request.env['fce.seal.number'].sudo().search([]),
            'bootstrap_formatting': True,
            'partner_id': order.partner_id.id,
            'booking_party': order.partner_id.fal_related_party_ids,
            'report_type': 'html',
            'action': order._get_portal_return_action(),
        }
        if order.company_id:
            values['res_company'] = order.company_id

        if order.has_to_be_paid():
            domain = expression.AND([
                ['&', ('state', 'in', ['enabled', 'test']), ('company_id', '=', order.company_id.id)],
                ['|', ('country_ids', '=', False), ('country_ids', 'in', [order.partner_id.country_id.id])]
            ])
            acquirers = request.env['payment.acquirer'].sudo().search(domain)

            values['acquirers'] = acquirers.filtered(lambda acq: (acq.payment_flow == 'form' and acq.view_template_id) or
                                                     (acq.payment_flow == 's2s' and acq.registration_view_template_id))
            values['pms'] = request.env['payment.token'].search([('partner_id', '=', order.partner_id.id)])
            values['acq_extra_fees'] = acquirers.get_acquirer_extra_fees(order.amount_total, order.currency_id, order.partner_id.country_id.id)

        if order.is_import:
            history = request.session.get('my_import_history', [])
        else:
            if order.state in ('draft', 'sent', 'cancel'):
                history = request.session.get('my_quotations_history', [])
            else:
                history = request.session.get('my_orders_history', [])
        values.update(get_records_pager(history, order))
        return values

    # Override
    @http.route(['/my/quotes', '/my/quotes/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_quotes(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sent', 'cancel']),
            ('is_import', '=', False),
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = SaleOrder.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/quotes",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_quotations_history'] = quotations.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': quotations.sudo(),
            'page_name': 'quote',
            'pager': pager,
            'default_url': '/my/quotes',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("sale.portal_my_quotations", values)

    @http.route(['/my/orders', '/my/orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'done']),
            ('is_import', '=', False),
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        order_count = SaleOrder.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/orders",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_orders_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'orders': orders.sudo(),
            'page_name': 'order',
            'pager': pager,
            'default_url': '/my/orders',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("sale.portal_my_orders", values)

    # Import Manifest

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        SaleOrder = request.env['sale.order']
        if 'import_manifest_count' in counters:
            values['import_manifest_count'] = SaleOrder.search_count([
                ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                # ('state', 'in', ['sent', 'cancel']),
                ('is_import', '=', True),
            ]) if SaleOrder.check_access_rights('read', raise_exception=False) else 0

        if 'quotation_count' in counters:
            values['quotation_count'] = SaleOrder.search_count([
                ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                ('state', 'in', ['sent', 'cancel']),
                ('is_import', '=', False),
            ]) if SaleOrder.check_access_rights('read', raise_exception=False) else 0
        if 'order_count' in counters:
            values['order_count'] = SaleOrder.search_count([
                ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                ('state', 'in', ['sale', 'done']),
                ('is_import', '=', False),
            ]) if SaleOrder.check_access_rights('read', raise_exception=False) else 0

        if 'invoiceimport_count' in counters:
            invoiceimpport_count = request.env['account.move'].search_count(self._get_invoicesimport_domain()) \
                if request.env['account.move'].check_access_rights('read', raise_exception=False) else 0
            values['invoiceimport_count'] = invoiceimpport_count
        return values

    @http.route(['/my/import_manifest', '/my/import_manifest/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_import(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            # ('state', 'in', ['sent', 'cancel']),
            ('is_import', '=', True),
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        import_manifest_count = SaleOrder.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/import_manifest",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=import_manifest_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        import_manifest = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_import_history'] = import_manifest.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': import_manifest.sudo(),
            'page_name': 'import_manifest',
            'pager': pager,
            'default_url': '/my/import_manifest',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("forecastle_module.portal_my_import", values)


    @http.route(['/my/orders/<int:order_id>'], type='http', auth="public", website=True)
    def portal_order_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        move = request.env['account.move'].search([('id', 'in', order_sudo.invoice_ids.ids), ('state', '!=', 'cancel')], limit=1)
        move2 = request.env['account.move'].search([('id', 'in', order_sudo.deposit_invoice_id.ids), ('state', '!=', 'cancel')], limit=1)
        move3 = request.env['account.move'].search([('id', 'in', order_sudo.deposit_detention_invoice_id.ids), ('state', '!=', 'cancel')], limit=1)
        _logger.info('xxxxxxxxxxxxxxxxxxxxxxxxx')
        _logger.info(move2)
        if order_sudo and order_sudo.is_import:
            if report_type == 'noa':
                return self._show_report(model=order_sudo, report_type='pdf', report_ref='forecastle_module.action_notice_of_arrival_final', download=download)
            elif report_type == 'spdo':
                return self._show_report(model=order_sudo, report_type='pdf', report_ref='forecastle_module.action_forecastle_pengantar_do_report', download=download)
            elif report_type == 'invoice':
                return self._show_report(model=move, report_type='pdf', report_ref='forecastle_module.action_forecastle_invoice', download=download)
            elif report_type == 'deposit':
                return self._show_report(model=move2, report_type='pdf', report_ref='forecastle_module.action_deposit_container', download=download)
            elif report_type == 'detention':
                return self._show_report(model=move3, report_type='pdf', report_ref='forecastle_module.action_deposit_invoice', download=download)
            # store the date as a string in the session to allow serialization
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_quote_%s' % order_sudo.id)
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_quote_%s' % order_sudo.id] = now
                body = _('Import manifest viewed by customer %s', order_sudo.partner_id.name)
                _message_post_helper(
                    "sale.order",
                    order_sudo.id,
                    body,
                    token=order_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=order_sudo.user_id.sudo().partner_id.ids,
                )

            values = self._order_get_page_view_values(order_sudo, access_token, **kw)
            values['message'] = message
            return request.render('forecastle_module.import_manifest_portal_template', values)
        else:
            if report_type == 'bc':
                return self._show_report(model=order_sudo, report_type='pdf', report_ref='forecastle_module.action_forecastle_booking', download=download)
            elif report_type == 'proforma':
                return self._show_report(model=order_sudo, report_type='pdf', report_ref='forecastle_module.action_forecastle_proforma_invoice', download=download)
            elif report_type == 'invoice':
                return self._show_report(model=move, report_type='pdf', report_ref='forecastle_module.action_forecastle_invoice', download=download)
            elif report_type == 'deposit':
                return self._show_report(model=move2, report_type='pdf', report_ref='forecastle_module.action_deposit_container', download=download)
            elif report_type == 'detention':
                return self._show_report(model=move3, report_type='pdf', report_ref='forecastle_module.action_deposit_invoice', download=download)
            else:
                return super().portal_order_page(order_id, report_type, access_token, message, download, **kw)

    @http.route(['/my/orders/<int:order_id>/importcontainerinfo'], type='http', auth="public", methods=['POST'], website=True)
    def importcontainerinfo(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        message_import_container_id = post.get('import_container_id', False)
        message_extend_do = post.get('import-extend-do', False)

        query_string = False
        charge_id = request.env['import.container.info'].sudo().browse(int(message_import_container_id))

        charge_id.sudo().write({'request_extend_do': message_extend_do})

        query_string = False
        return request.redirect(order_sudo.get_portal_url(query_string=query_string))


    @http.route(['/my/orders/<int:order_id>/uploadrefunddocument'], type='http', auth="public", methods=['POST'], website=True)
    def uploadrefunddocument(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        today = date.today()


        documents = {}
        message_upload_ktp = post.get('upload_ktp', False)
        if message_upload_ktp:
            file_ktp = message_upload_ktp.read()
            file_ktp_base64 = base64.encodebytes(file_ktp)
            documents.update({
                'ktp': file_ktp_base64,
                'filename_ktp': message_upload_ktp.filename,
                'ktp_date_submit': today
            })

        message_upload_surat_kuasa = post.get('upload_surat_kuasa', False)
        if message_upload_surat_kuasa:
            file_surat_kuasa = message_upload_surat_kuasa.read()
            file_surat_kuasa_base64 = base64.encodebytes(file_surat_kuasa)
            documents.update({
                'surat_kuasa': file_surat_kuasa_base64,
                'filename_surat_kuasa': message_upload_surat_kuasa.filename,
                'surat_kuasa_date_submit': today
            })

        message_upload_bl = post.get('upload_bl', False)
        if message_upload_bl:
            file_bl = message_upload_bl.read()
            file_bl_base64 = base64.encodebytes(file_bl)
            documents.update({
                'bl': file_bl_base64,
                'filename_bl': message_upload_bl.filename,
                'bl_date_submit': today
            })

        message_upload_eir = post.get('upload_eir', False)
        if message_upload_eir:
            file_eir = message_upload_eir.read()
            file_eir_base64 = base64.encodebytes(file_eir)
            documents.update({
                'eir': file_eir_base64,
                'filename_eir': message_upload_eir.filename,
                'eir_date_submit': today
            })

        message_upload_sp2 = post.get('upload_sp2', False)
        if message_upload_sp2:
            file_sp2 = message_upload_sp2.read()
            file_sp2_base64 = base64.encodebytes(file_sp2)
            documents.update({
                'sp2': file_sp2_base64,
                'filename_sp2': message_upload_sp2.filename,
                'sp2_date_submit': today
            })

        message_upload_bukti_bayar = post.get('upload_bukti_bayar', False)
        if message_upload_bukti_bayar:
            file_bukti_bayar = message_upload_bukti_bayar.read()
            file_bukti_bayar_base64 = base64.encodebytes(file_bukti_bayar)
            documents.update({
                'bukti_bayar': file_bukti_bayar_base64,
                'filename_bukti_bayar': message_upload_bukti_bayar.filename,
                'bukti_bayar_date_submit': today
            })

        message_upload_official_receipt = post.get('upload_official_receipt', False)
        if message_upload_official_receipt:
            file_official_receipt = message_upload_official_receipt.read()
            file_official_receipt_base64 = base64.encodebytes(file_official_receipt)
            documents.update({
                'official_receipt': file_official_receipt_base64,
                'filename_official_receipt': message_upload_official_receipt.filename,
                'official_receipt_date_submit': today
            })

        message_upload_invoice_detention = post.get('upload_invoice_detention', False)
        if message_upload_invoice_detention:
            file_invoice_detention = message_upload_invoice_detention.read()
            file_invoice_detention_base64 = base64.encodebytes(file_invoice_detention)
            documents.update({
                'invoice_detention': file_invoice_detention_base64,
                'filename_invoice_detention': message_upload_invoice_detention.filename,
                'invoice_detention_date_submit': today
            })

        message_upload_official_receipt_detention = post.get('upload_official_receipt_detention', False)
        if message_upload_official_receipt_detention:
            file_official_receipt_detention = message_upload_official_receipt_detention.read()
            file_official_receipt_detention_base64 = base64.encodebytes(file_official_receipt_detention)
            documents.update({
                'official_receipt_detention': file_official_receipt_detention_base64,
                'filename_official_receipt_detention': message_upload_official_receipt_detention.filename,
                'official_receipt_detention_date_submit': today
            })

        order_sudo.sudo().write(documents)

        query_string = False
        return request.redirect(order_sudo.get_portal_url(query_string=query_string))

    def _get_invoices_domain(self):
        return [('move_type', 'in', ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')), ('fal_sale_source_id.is_import', '=', False)]

    # Override
    @http.route(['/my/invoices', '/my/invoices/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_invoices(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        AccountInvoice = request.env['account.move']

        domain = self._get_invoices_domain()

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'invoice_date desc'},
            'duedate': {'label': _('Due Date'), 'order': 'invoice_date_due desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'invoices': {'label': _('Invoices'), 'domain': [('move_type', '=', ('out_invoice', 'out_refund'))]},
            'bills': {'label': _('Bills'), 'domain': [('move_type', '=', ('in_invoice', 'in_refund'))]},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        invoice_count = AccountInvoice.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/invoices",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=invoice_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        invoices = AccountInvoice.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_invoices_history'] = invoices.ids[:100]

        values.update({
            'date': date_begin,
            'invoices': invoices,
            'page_name': 'invoice',
            'pager': pager,
            'default_url': '/my/invoices',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby':filterby,
        })
        return request.render("account.portal_my_invoices", values)


    def _get_invoicesimport_domain(self):
        return [('move_type', 'in', ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')), ('fal_sale_source_id.is_import', '=', True)]

    @http.route(['/my/invoicesimport', '/my/invoicesimport/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_invoices_import(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        AccountInvoice = request.env['account.move']

        domain = self._get_invoicesimport_domain()

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'invoice_date desc'},
            'duedate': {'label': _('Due Date'), 'order': 'invoice_date_due desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'invoices': {'label': _('Invoices'), 'domain': [('move_type', '=', ('out_invoice', 'out_refund'))]},
            'bills': {'label': _('Bills'), 'domain': [('move_type', '=', ('in_invoice', 'in_refund'))]},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]


        domain += [('fal_sale_source_id.is_import', '=', True)]

        # count for pager
        invoice_count = AccountInvoice.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/invoices",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=invoice_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        invoices = AccountInvoice.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_invoices_history'] = invoices.ids[:100]

        values.update({
            'date': date_begin,
            'invoices': invoices,
            'page_name': 'invoice_import',
            'pager': pager,
            'default_url': '/my/invoicesimport',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby':filterby,
        })
        return request.render("account.portal_my_invoices", values)
