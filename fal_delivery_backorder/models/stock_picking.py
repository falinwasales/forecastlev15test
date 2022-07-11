from odoo import fields, models, api, _


class Picking(models.Model):
    _inherit = "stock.picking"


    def fal_action_create_backorder(self):
        view = self.env.ref('fal_delivery_backorder.fal_view_backorder_wizard')
        backorder_line_ids = []
        for p in self:
            backorder_line_ids = [(0, 0, {'move_line_id': m.id}) for m in p.move_lines]
        wiz = self.env['fal.stock.backorder.wizard'].create({'pick_ids': [(4, p.id) for p in self], 'fal_stock_backorder_line_wizard_ids': backorder_line_ids})
        return {
            'name': _('Create Backorder'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'fal.stock.backorder.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }
