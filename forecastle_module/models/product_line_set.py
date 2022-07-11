from odoo import fields, models
from odoo.tools import safe_eval


class ProductSet(models.Model):
    _inherit = "product.set"

    principal_id = fields.Many2one(
        comodel_name="res.partner",
        required=False,
        ondelete="cascade",
        index=True,
        help="You can attached the set to a specific principal "
        "or no one. If you don't specify one, "
        "it's going to be available for all of them.",
        domain=[("is_principal", "=", True)],
    )
    customer_portal_edit = fields.Boolean("Customer Can Edit in Portal")

    create_uid = fields.Many2one('res.users',string='Created By', default=lambda self: self.env.user.id)


class ProductSetLine(models.Model):
    _inherit = "product.set.line"

    formula = fields.Char("Formula", help="If Formula is set, it will be used to calculate quantity applied")

    def prepare_sale_order_line_values(self, order, quantity, max_sequence=0):
        self.ensure_one()
        result = super(ProductSetLine, self).prepare_sale_order_line_values(order, quantity, max_sequence)
        if self.formula:
            result['product_uom_qty'] = safe_eval.safe_eval(self.formula, {'base_qty': self.quantity, 'qty': quantity})
        return result
