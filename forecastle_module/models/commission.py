# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class CommissionExport(models.Model):
    _name = 'commission.export'

    def name_get(self):
        res = []
        for commission in self:
            res.append((commission.id, "%s - %s" % (commission.principal_id.name, commission.customer_status)))
        return res

    principal_id = fields.Many2one(
        'res.partner', domain="[('is_principal', '=', True)]",
        string="Principal", required=True)
    customer_status = fields.Selection([
        ('general', 'General'),
        ('inhouse', 'Inhouse'),
        ('nomination', 'Nomination'),
    ], string="Customer Status", default='general', required=True)

    commission_line_ids = fields.One2many(
        'commission.export.line', 'commission_export_id',
        string="Comission Line")
    active = fields.Boolean(default=False)

    def action_approve(self):
        for commission in self:
            commission.active = True


class CommissionExportLine(models.Model):
    _name = 'commission.export.line'

    commission_export_id = fields.Many2one('commission.export')

    @api.onchange('commission_type')
    def _onchange_commission_type(self):
        res = {}
        if self.commission_type == 'detention':
            res['domain'] = {'product_ids': [('is_detention', '=', True)]}
        return res

    commission_type = fields.Selection([
        ('export', 'Export'),
        ('import', 'Import'),
        ('detention', 'Detention'),
    ], string="Comission Type")
    product_category_id = fields.Many2one(
        'product.category', string="Product Container", required=True
    )
    product_ids = fields.Many2many(
        'product.product', string="Charge Item", required=True)
    percentage = fields.Float(string="Percentage")
    minimum_value = fields.Float(string="Minimum Value")
    fix_price = fields.Float(string="Fixed Price")
    tax_ids = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    use_formula = fields.Boolean(string="Use Formula")
    python_formula = fields.Text(string="Formula", default="result=0", help='''
# Available variables:
#----------------------
# lines
# total_amount
# commission_line
#----------------------
# result
''')

    # Python Code
    def _run_python_formula(self, lines, total_amount):
        pod = lines[0].order_id.sales_source_id.pod_id.coutry_id.name
        ctx = dict(self._context)
        localdict = {
            **{
                'lines': lines,
                'commission_line': self,
                'total_amount': total_amount,
                'pod_id': pod,
                'result': 0,

            }
        }
        if self.python_formula:
            try:
                safe_eval(self.python_formula, localdict, mode='exec', nocopy=True)
                return localdict['result']
            except Exception as e:
                raise UserError(_('Wrong python Code'))
        return False
