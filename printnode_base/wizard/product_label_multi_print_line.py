# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, exceptions, _


class ProductLabelMultiPrintLine(models.TransientModel):
    _name = 'product.label.multi.print.line'
    _description = 'Print Product Labels / Line'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
    )

    quantity = fields.Integer(
        required=True,
        default=1,
    )

    wizard_id = fields.Many2one(
        comodel_name='product.label.multi.print',
    )

    @api.constrains('quantity')
    def _check_quantity(self):
        for rec in self:
            if rec.quantity < 1:
                raise exceptions.ValidationError(
                    _(
                        'Quantity can not be less than 1 for product {product}'
                    ).format(**{
                        'product': rec.product_id.display_name,
                    })
                )
