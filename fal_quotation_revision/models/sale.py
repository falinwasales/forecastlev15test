# -*- coding: utf-8 -*-
from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _order_revised_count(self):
        fal_order_revised_count = self.env['sale.order'].search(
            [('parent_id', 'parent_of', self.id), ('active', '=', False), ('id', '!=', self.id)])
        self.fal_order_revised_count = len(fal_order_revised_count)

    name = fields.Char(string='Order Reference', required=True, copy=False,
                       readonly=True, index=True, default='New')
    parent_id = fields.Many2one(
        'sale.order', 'Parent SaleOrder', copy=False)
    fal_order_revised_count = fields.Integer(
        '# of Orders Revised', compute='_order_revised_count', copy=False)
    fal_so_number = fields.Integer('SO Number', copy=False, default=1)
    is_revised_so = fields.Boolean(string="Is Revised Order", default=False)

    ###########################################################################
    # Function
    # Make Revision
    def so_revision_quote(self):
        for cur_rec in self:
            if not cur_rec.origin:
                origin_name = cur_rec.name
                cur_rec.origin = cur_rec.name
            else:
                origin_name = cur_rec.origin
            # Create a new SO (to be used)
            vals = {
                'name': origin_name,
                'state': 'draft',
                'parent_id': cur_rec.id,
                'fal_so_number': cur_rec.fal_so_number + 1
            }
            new_rec = cur_rec.copy(default=vals)

            # Inactive the old record
            cur_rec.name = origin_name + ' v' + str(cur_rec.fal_so_number)
            cur_rec.is_revised_so = True
            cur_rec.active = False

            action = self.env.ref('sale.action_quotations_with_onboarding').read()[0]
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = new_rec.id
            return action

    # We restore odoo feature, because it's annoying to always need to sent quotation by 
    # email before we got into sent state. Sometimes we only print
    def print_quotation(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})

        return self.env.ref('sale.action_report_saleorder')\
            .with_context(discard_logo_check=True).report_action(self)
