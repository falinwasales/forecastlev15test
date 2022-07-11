# -*- coding: utf-8 -*-
from odoo import fields, models, _, api
from odoo.tools import float_repr
from datetime import datetime
from itertools import chain


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    start_date = fields.Date(string="Start Date")
    date_validity = fields.Date(string="Validity Date")
    pol_id = fields.Many2one('fce.port.code', string="POL")
    pod_id = fields.Many2one('fce.port.code', string="POD")
    carrier_id = fields.Many2one('res.partner', string="Feeder Slot", domain="[('is_vendor', '=', True)]")
    principal_id = fields.Many2one('res.partner', string="Principal", domain="[('is_principal', '=', True)]")
    partner_id = fields.Many2one('res.partner', string="Customer", domain="[('is_customer', '=', True)]")
    active = fields.Boolean(default=False)
    visible_button = fields.Boolean(default=False, copy=False)
    idr_price = fields.Char('Type', compute='domain_idr')
    reference_number = fields.Char(string="Reference Number")
    item_ids = fields.One2many(
        'product.pricelist.item', 'pricelist_id', 'Pricelist Items', context={'active_test': False}, copy=True)
    fal_price_id = fields.Many2one('product.pricelist', string="Price", copy=False)

    discount_policy = fields.Selection(
        default='without_discount')

    @api.depends('currency_id')
    def domain_idr(self):
        self.idr_price = False
        for x in self:
            if x.currency_id.name == 'IDR':
                x.idr_price = 'IDR'

    def action_auto_crete(self):
        pricelist_idr = self.copy(default={'currency_id': self.env.ref('base.IDR').id, 'visible_button': True})
        for item in pricelist_idr.item_ids:
            item.write({'compute_price': 'formula', 'base': 'pricelist', 'base_pricelist_id': self.id})
        self.fal_price_id = pricelist_idr
        self.visible_button = True
        if self.fal_price_id:
            self.fal_price_id.fal_price_id = self.id

    def action_approve(self):
        for pricelist in self:
            pricelist.active = True
            pricelist.fal_price_id.active = True
            # if pricelist.active:
            #     pricelist.action_auto_crete()

    # FORECASTLE ADDON
    # Adding Filter by Product SET
    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        """ Low-level method - Mono pricelist, multi products
        Returns: dict{product_id: (price, suitable_rule) for the given pricelist}

        Date in context can be a date, datetime, ...

            :param products_qty_partner: list of typles products, quantity, partner
            :param datetime date: validity date
            :param ID uom_id: intermediate unit of measure
        """
        self.ensure_one()
        if not date:
            date = self._context.get('date') or fields.Datetime.now()
        if not uom_id and self._context.get('uom'):
            uom_id = self._context['uom']
        if uom_id:
            # rebrowse with uom if given
            products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
            products_qty_partner = [(products[index], data_struct[1], data_struct[2]) for index, data_struct in enumerate(products_qty_partner)]
        else:
            products = [item[0] for item in products_qty_partner]

        if not products:
            return {}

        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = list(categ_ids)

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in
                        list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        sale_line_product_set = self._context.get('product_set', self._context.get('set', self._context.get('wizard_set', False)))

        items = self.with_context(set=sale_line_product_set)._compute_price_rule_get_items(products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids)

        results = {}
        for product, qty, partner in products_qty_partner:
            results[product.id] = 0.0
            suitable_rule = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = self._context.get('uom') or product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = self.env['uom.uom'].browse([self._context['uom']])._compute_quantity(qty, product.uom_id)
                except UserError:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass

            # if Public user try to access standard price from website sale, need to call price_compute.
            # TDE SURPRISE: product can actually be a template
            price = product.price_compute('list_price')[product.id]

            price_uom = self.env['uom.uom'].browse([qty_uom_id])
            for rule in items:
                if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and not (product.product_variant_count == 1 and product.product_variant_id.id == rule.product_id.id):
                        # product rule acceptable on template if has only one variant
                        continue
                else:
                    if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue
                # Product Set Check
                if rule.product_set_id and sale_line_product_set and not (sale_line_product_set.id == rule.product_set_id.id):
                    # product rule acceptable on template if has only one variant
                    continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                if rule.base == 'pricelist' and rule.base_pricelist_id:
                    price_tmp = rule.base_pricelist_id._compute_price_rule([(product, qty, partner)], date, uom_id)[product.id][0]  # TDE: 0 = price, 1 = rule
                    price = rule.base_pricelist_id.currency_id._convert(price_tmp, self.currency_id, self.env.company, date, round=False)
                else:
                    # if base option is public price take sale price else cost price of product
                    # price_compute returns the price in the context UoM, i.e. qty_uom_id
                    price = product.price_compute(rule.base)[product.id]

                if price is not False:
                    price = rule._compute_price(price, price_uom, product, quantity=qty, partner=partner)
                    suitable_rule = rule
                break

            # Final price conversion into pricelist currency
            if suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
                if suitable_rule.base == 'standard_price':
                    cur = product.cost_currency_id
                else:
                    cur = product.currency_id
                price = cur._convert(price, self.currency_id, self.env.company, date, round=False)

            if not suitable_rule:
                cur = product.currency_id
                price = cur._convert(price, self.currency_id, self.env.company, date, round=False)

            results[product.id] = (price, suitable_rule and suitable_rule.id or False)
        return results


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    # Product Set
    product_set_id = fields.Many2one('product.set', 'Product Set')
    # Date need to be the same as pricelist
    date_start = fields.Date(string="Start Date", related="pricelist_id.start_date", store=True, readonly=True)
    date_end = fields.Date(string="End Date", related="pricelist_id.date_validity", store=True, readonly=True)
    applied_on = fields.Selection(default='1_product')


class ProductPricelistChatter(models.Model):
    _name = 'product.pricelist'
    _inherit = ['product.pricelist', 'mail.thread', 'mail.activity.mixin']
