from odoo import _, exceptions, fields, models, api
from datetime import date
from dateutil.relativedelta import relativedelta, MO, SU


class FceSoaWizard(models.TransientModel):
    _name = 'fce.soa.wizard'
    _description = 'FCE SOA Wizard'

    def default_soa_id(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            soa_id = self.env['fce.soa'].browse(active_id)
            return soa_id.id
        return False

    def default_soa_line_ids(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            soa_id = self.env['fce.soa'].browse(active_id)
            return soa_id.soa_line_ids.filtered(lambda x: x.fce_exclude).ids
        return False

    fal_soa_id = fields.Many2one('fce.soa', string="Source Location", default=default_soa_id)
    soa_line_ids_wizard = fields.Many2many('account.move.line', string="SOA Line", default=default_soa_line_ids)

    def process(self):
        self.fal_soa_id._create_journal_entries()
        for line in self.soa_line_ids_wizard:
            date_calculate = line.move_id.invoice_date + relativedelta(months=1)
            line.move_id.write({'invoice_date': date_calculate})
            line.write({'date': date_calculate,
                        'date_maturity': date_calculate})
