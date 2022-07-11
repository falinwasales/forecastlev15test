from odoo import models, fields, api, _


class HrApplicant(models.Model):
    _name = 'hr.applicant'
    _inherit = ['hr.applicant']

    def hr_applicant_whatsapp(self):
        record_phone = self.partner_mobile
        if not record_phone[0] == "+":
            view = self.env.ref('odoo_whatsapp_integration.warn_message_wizard')
            view_id = view and view.id or False
            context = dict(self._context or {})
            context['message'] = "Please add a valid mobile number along with country code!"
            return {
                'name': 'Invalid Mobile Number',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'display.error.message',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': context
            }
        else:
            return {'type': 'ir.actions.act_window',
                    'name': _('Whatsapp Message'),
                    'res_model': 'whatsapp.wizard.applicant',
                    'target': 'new',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': {
                        'default_template_id': self.env.ref('odoo_whatsapp_integration.whatsapp_hr_applicant_wizard').id},
                    }

    @api.onchange('partner_mobile', 'country_id', 'company_id')
    def _onchange_mobile(self):
        if self.partner_mobile:
            self.partner_mobile = self.phone_format(self.partner_mobile)

    # overide here
    def _inverse_partner_mobile(self):
        for x in self:
            x.partner_mobile = x.phone_format(x.partner_mobile)
        for applicant in self.filtered(lambda a: a.partner_id and a.partner_mobile and not a.partner_id.mobile):
            applicant.partner_id.mobile = applicant.partner_mobile
