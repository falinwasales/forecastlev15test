from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_set_id = fields.Many2one('product.set', string="Product Set ID")
    product_set_qty = fields.Float("Product Set Qty")
    do_not_merge = fields.Boolean("Do Not Merge")

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        res['product_set_id'] = self.product_set_id.id
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    product_set_id = fields.Many2one('product.set', string="Product Set ID")


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def _compute_price_rule_get_items(self, products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids):
        self.ensure_one()
        if self._context.get('set'):
            # Load all rules
            self.env['product.pricelist.item'].flush(['price', 'currency_id', 'company_id'])
            self.env.cr.execute(
                """
                SELECT
                    item.id
                FROM
                    product_pricelist_item AS item
                LEFT JOIN product_category AS categ ON item.categ_id = categ.id
                WHERE
                    (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))
                    AND (item.product_id IS NULL OR item.product_id = any(%s))
                    AND (item.categ_id IS NULL OR item.categ_id = any(%s))
                    AND (item.pricelist_id = %s)
                    AND (item.product_set_id IS NULL OR item.product_set_id=%s)
                ORDER BY
                    item.applied_on, item.min_quantity desc, categ.complete_name desc, item.id desc
                """,
                (prod_tmpl_ids, prod_ids, categ_ids, self.id, self._context.get('set').id))
            # NOTE: if you change `order by` on that query, make sure it matches
            # _order from model to avoid inconstencies and undeterministic issues.

            item_ids = [x[0] for x in self.env.cr.fetchall()]
            return self.env['product.pricelist.item'].browse(item_ids)
        else:
            return super(Pricelist, self)._compute_price_rule_get_items(products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids)
