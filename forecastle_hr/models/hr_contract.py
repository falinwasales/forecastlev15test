# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class HrContract(models.Model):
    _inherit = "hr.contract"

    employment_status = fields.Selection([
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
        ('contract', 'Contract'),
        ('probation', 'Probation'),
        ('permanent', 'Permanent'),
    ], string="Contract Type")

    contract_duration = fields.Selection([
        ('3_month', '3 Months'),
        ('6_month', '6 Months'),
        ('12_month', '12 Months'),
    ], string="Contract Duration")

    @api.onchange('contract_duration', 'date_start')
    def _onchange_contract_duration(self):
        if self.contract_duration and self.date_start:
            end_date = False
            if self.contract_duration == '3_month':
                end_date = self.date_start + relativedelta(months=3)
            elif self.contract_duration == '6_month':
                end_date = self.date_start + relativedelta(months=6)
            elif self.contract_duration == '12_month':
                end_date = self.date_start + relativedelta(months=12)
            self.date_end = end_date
