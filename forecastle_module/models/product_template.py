# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    deposit_price = fields.Float(string="Deposit Price")
    account_container_deposit_id = fields.Many2one('account.account', string="Account Container Deposit")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_container = fields.Boolean("Container Product", help="Technical field to help create CRO lines in Sales Order")
    is_telex = fields.Boolean("Telex")
    is_detention = fields.Boolean("Detention")
    is_interim_product = fields.Boolean("Interim")
    is_ofr = fields.Boolean("OFR")
    is_dollar = fields.Boolean("Dollar")
    is_ehs_comision = fields.Boolean("EHS Commision")
    is_upsale = fields.Boolean("Upsale")
    import_charge = fields.Boolean("Import Charge")
    container_size = fields.Char(string="Container Size")
    container_type = fields.Selection([
        ('gp', 'GP'),
        ('hc', 'HC'),
        ('tunne', 'Tunne Type'),
        ('ot', 'OT'),
        ('fr', 'FR'),
        ('reefer', 'RF'),
        ('rh', 'RH'),
        ('barge', 'Barge Container'),
        ('breakbulk', 'Bulk Container'),
        ('tk', 'TK'),
        ('other', 'Other')
    ], "Container Type")
    principal_id = fields.Many2one('res.partner', domain="[('is_principal', '=', True)]")
    account_container_deposit_id = fields.Many2one('account.account', string="Account Container Deposit")
    ofr_import = fields.Float(string="OFR Import")
    is_gain_forex = fields.Boolean("Gain Forex")
    is_loss_forex = fields.Boolean("Loss Forex")


class SupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    percentage = fields.Float('Sales %', help="In a case that purchase price is the same as sales price, this field is used to define the percentage of sales to purchase ratio")
