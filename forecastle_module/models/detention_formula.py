# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from dateutil.relativedelta import relativedelta


class DetentionFormula(models.Model):
    _name = "detention.formula"

    name = fields.Char(string="Description", required=True)
    free_time = fields.Selection([('day7', '7'), ('day14', '14'), ('day21', '21')], string="Free Time")
    principal_id = fields.Many2one('res.partner', string="Principal")
    product_category = fields.Many2one('product.category', string="Product Category")
    unit_price = fields.Float(string="Unit Price")
    python_formula = fields.Text(string="Formula", help='''
# Available variables:
#----------------------
# detention
# container
# set values
#----------------------
# non_slab
# slab1
# slab2
# slab3
# slab4
# actual_detention_charge
''')
    remarks = fields.Char(string="Remarks")

    slab1 = fields.Float(string='Slab1')
    slab2 = fields.Float(string='Slab2')
    slab3 = fields.Float(string='Slab3')
    slab4 = fields.Float(string='Slab4')

    slab_value1 = fields.Float(string='Slab Value 1')
    slab_value2 = fields.Float(string='Slab Value 2')
    slab_value3 = fields.Float(string='Slab Value 3')
    slab_value4 = fields.Float(string='Slab Value 4')

    # Python Code
    def _run_python_formula(self, container):
        ctx = dict(self._context)
        localdict = {
            **{
                'detention': self,
                'container': container,
                'non_slab': 0,
                'slab1': 0,
                'slab2': 0,
                'slab3': 0,
                'slab4': 0,
                'actual_detention_charge': 0,
            }
        }
        if self.python_formula:
            try:
                safe_eval(self.python_formula, localdict, mode='exec', nocopy=True)
                return localdict
            except Exception as e:
                raise UserError(_('Wrong python Code'))
        return False
