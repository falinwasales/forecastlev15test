# -*- coding: utf-8 -*-
# Part of CLuedoo. See LICENSE file for full copyright and licensing details.
from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def webclient_rendering_context(self):
        """ Overrides community to prevent unnecessary load_menus request """
        return {
            'session_info': self.session_info(),
        }

    # def session_info(self):
    #     user = request.env.user
    #     result = super(IrHttp, self).session_info()
    #     if self.env.user.has_group('base.group_user'):
    #         # Make a mapping of company and it's business type
    #         # So if user change business type, it should change company
    #         company_mapping = []
    #         for company, company_name in result['user_companies']['allowed_companies']:
    #             company_id = request.env['res.company'].browse(company)
    #             for ou in company_id.operating_unit_ids.filtered(lambda x: x.id in user.operating_unit_ids.ids):
    #                 company_mapping.append((company_id.id, ou.id))
    #         result.update({
    #             "user_operating_units": {'current_operating_unit': (user.default_operating_unit_id.id, user.default_operating_unit_id.name), 'assigned_operating_units': [(aou.id, aou.name) for aou in user.assigned_operating_unit_ids], 'operating_units': [(ou.id, ou.name) for ou in user.set_operating_unit_ids]},
    #             "display_switch_operating_unit_menu": len(user.operating_unit_ids) > 0,
    #             "company_operating_unit_map": company_mapping,
    #         })
    #     return result
