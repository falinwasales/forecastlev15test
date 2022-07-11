# Copyright 2015 Anybox S.A.S
# Copyright 2016-2020 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, exceptions, fields, models


class ProductSetAdd(models.TransientModel):
    _inherit = "product.set.add"

    principal_id = fields.Many2one(related="order_id.principal_id", ondelete="cascade")
    imp_principal_id = fields.Many2one(related="order_id.imp_principal_id", ondelete="cascade")


class SetOfr(models.Model):
    _name = 'set.ofr.wizard'

    ofr_line_ids = fields.One2many('set.ofr.line.wizard', 'set_ofr_id')

    def set_ofr(self):
        for line in self.ofr_line_ids:
            for con in line.container_info_ids:
                con.write({'ofr': line.total_price})


class SetOfrLine(models.Model):
    _name = 'set.ofr.line.wizard'

    product_id = fields.Many2one('product.product', domain="[('is_container', '=', True)]", string="Container")
    qty = fields.Float(string="Quantity", default=1)
    total_price = fields.Float(string="Total Price")
    container_info_ids = fields.Many2many('import.container.info')
    set_ofr_id = fields.Many2one('set.ofr.wizard')
