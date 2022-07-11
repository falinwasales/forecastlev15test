# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import models


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'multi.print.mixin']

    def _add_multi_print_lines(self):
        products = self.mapped('product_variant_ids')
        return super(ProductTemplate, self)._add_multi_print_lines(records=products)
