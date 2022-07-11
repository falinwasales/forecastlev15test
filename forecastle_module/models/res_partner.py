import logging
import ast
import re
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Flag for Forecastle
    is_customer = fields.Boolean(string="Is Customer")
    is_vendor = fields.Boolean(string="Is Feeder Slot")
    is_principal = fields.Boolean(string="Is Principal")
    is_carrier = fields.Boolean(string="Is Feeder Operator")
    is_shipper = fields.Boolean(string="Is Shipper")
    is_consignee = fields.Boolean(string="Is Consignee")
    is_notify = fields.Boolean(string="Is Notify")
    is_agent = fields.Boolean(string="Is Agent")
    is_depot = fields.Boolean(string="Is Depot")
    is_forwarder = fields.Boolean(string="Is Forwarder")
    is_vendor_expense = fields.Boolean(string="Vendor Expense")
    vat = fields.Char(string='You must fill the vat', index=True, help="The Tax Identification Number. Complete it if the contact is subjected to government taxes. Used in some legal statements.")
    initial_bl = fields.Char(string="Initial BL")
    agent_code = fields.Char(string="Agent Code")
    principal_code = fields.Char(string="Principal Code")
    depot_code = fields.Char(string="Depot Code")
    feeder_code = fields.Char(string="Feeder Code")
    country_code = fields.Char(string='Country Code', related='country_id.code')

    virtual_account = fields.Char(string='Virtual Account')

    # Pricipal
    fal_principal_ids = fields.Many2many('res.partner', 'fal_partner_principal_rel', 'principal_id', 'partner_id', domain=[('is_principal', '=', True)], string='Principal')
    fal_agent_code_ids = fields.One2many('fce.agent.code', 'principal_id', string='Partner Code')

    # Report Template
    draft_bl_report_id = fields.Many2one('ir.actions.report', 'Draft BL Report')

    fal_related_party_ids = fields.Many2many('res.partner', 'fal_partner_related_party_rel', 'related_party_id', 'partner_id', string='Related Party')
    fal_shipper_ids = fields.Many2many('res.partner', 'fal_partner_shipper_rel', 'shipper_id', 'partner_id', domain=[('is_shipper', '=', True)], string='Shipper')
    fal_consignee_ids = fields.Many2many('res.partner', 'fal_partner_consignee_rel', 'consignee_id', 'partner_id', domain=[('is_consignee', '=', True)], string='Consignee')
    fal_notify_ids = fields.Many2many('res.partner', 'fal_partner_notify_rel', 'notify_id', 'partner_id', domain=[('is_notify', '=', True)], string='Notify')

    # dont update vat, override
    def _update_fields_values(self, fields):
        """ Returns dict of write() values for synchronizing ``fields`` """
        values = {}
        for fname in fields:
            if fname != 'vat':
                field = self._fields[fname]
                if field.type == 'many2one':
                    values[fname] = self[fname].id
                elif field.type == 'one2many':
                    raise AssertionError(_('One2Many fields cannot be synchronized as part of `commercial_fields` or `address fields`'))
                elif field.type == 'many2many':
                    values[fname] = [(6, 0, self[fname].ids)]
                else:
                    values[fname] = self[fname]
        return values

    @api.constrains('vat')
    def _check_vat_unique(self):
        for record in self:
            if record.vat:
                vat_find = self.search([('vat', '=', self.vat)])
                if len(vat_find) >= 2:
                    same_partner = vat_find.filtered(lambda a: a.id != record.id)
                    raise ValidationError(_('The vat that you type is already taken by %s' % (same_partner and same_partner[0].display_name)))

    property_principal_account_payable_id = fields.Many2one('account.account', company_dependent=True,
        string="Principal Account Payable",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]")
    property_principal_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
        string="Principal Account Receivable",
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]")

    property_principal_account_interim_ap = fields.Many2one('account.account', company_dependent=True,
        string="Interim Account Payable",
        domain="[('deprecated', '=', False), ('company_id', '=', current_company_id)]")
    property_principal_account_interim_ar = fields.Many2one('account.account', company_dependent=True,
        string="Interim Account Receivable",
        domain="[('deprecated', '=', False), ('company_id', '=', current_company_id)]")

    # For commission Export
    product_commission_id = fields.Many2one('product.product', string="Product Commission")

    @api.onchange(
        'is_customer', 'is_vendor', 'is_principal',
        'is_carrier', 'is_shipper', 'is_consignee',
        'is_notify', 'is_agent', 'is_depot', 'is_forwarder', 'is_vendor_expense')
    def _onchange_get_customer_supplier_rank(self):
        if self.is_customer or self.is_shipper or self.is_consignee or self.is_notify or self.is_vendor_expense:
            self.customer_rank = 1
        else:
            self.customer_rank = 0

        if self.is_depot or self.is_forwarder or self.is_vendor or self.is_principal or self.is_carrier or self.is_agent:
            self.supplier_rank = 1
        else:
            self.supplier_rank = 0

    @api.model
    def get_address(self, contact_fix):
        contact = self.env['res.partner'].search([('id', '=', contact_fix)]).street
        return contact

    @api.model
    def unlink_address(self, contact_id, sale_id):
        contact = self.env['res.partner'].search([('id', '=', contact_id)])
        sale_obj = self.env['sale.order'].search([('id', '=', sale_id)])
        if contact:
            sales_contact = sale_obj.partner_id.fal_related_party_ids.filtered(lambda ct: ct.id != contact.id)
            sale_obj.partner_id.write({'fal_related_party_ids': [(6, 0, sales_contact.ids)]})
        return contact, sale_obj


class ResCompany(models.Model):
    _inherit = 'res.company'

    forecastle_code = fields.Char(string="Branch Code")
    soa_gain_account_id = fields.Many2one('account.account', domain="[('deprecated', '=', False), ('company_id', '=', id)]",)
    fal_logo_invoice = fields.Image(string='Companies Logo(Invoices)')
    fal_company_logo = fields.Image(string='Companies Logo(Telex)')


class OperatingUnit(models.Model):
    _inherit = "operating.unit"

    forecastle_code = fields.Char(string="Branch Code")
