# -*- coding: utf-8 -*-
 
from odoo import models, fields, api, exceptions, _

 
class SaleWizard(models.Model):
    _inherit = 'sale.order'
 
 
    def get_pre_alert_report(self):
        # redirect ke controller /sale/excel_report untuk generate file excel
        return {
            'type': 'ir.actions.act_url',
            'url': '/sale/pre_alert/%s' % (self.id),
            'target': 'new',
        }

    def get_shipping_report(self):
        # redirect ke controller /sale/excel_report untuk generate file excel
        return {
            'type': 'ir.actions.act_url',
            'url': '/sale/shipping_instruction/%s' % (self.id),
            'target': 'new',
        }

    def get_final_shipping_report(self):
        # redirect ke controller /sale/excel_report untuk generate file excel
        return {
            'type': 'ir.actions.act_url',
            'url': '/sale/final_shipping_instruction/%s' % (self.id),
            'target': 'new',
        }