# Copyright 2020 VentorTech OU
# License OPL-1.0 or later.

from odoo import api, SUPERUSER_ID


EXTERNAL_IDS = {
    'sale.model_sale_order': ('action_confirm', 'printnode_base.sale_order_action_confirm'),
    'stock.model_stock_picking': ('button_validate', 'printnode_base.transfer_button_validate'),
}


def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        adds = {'active_test': False}

        env['printnode.action.method'].search([
            '|', '|',
            ('model_id', '=', False),
            ('name', '=', False),
            ('method', '=', False),
        ]).unlink()
        env['printnode.action.button'].with_context(**adds).search([
            '|', '|',
            ('method_id', '=', False),
            ('model_id', '=', False),
            ('report_id', '=', False),
        ]).unlink()

        method_duplicates = env['printnode.action.method'].read_group(
            domain=[], fields=['model_id', 'method'], groupby=['model_id', 'method'], lazy=False)

        # [{
        #     '__count': 2,
        #     'model_id': (462, <odoo.tools.func.lazy object at 0x7f5c210346c0>),
        #     'method': 'button_validate',
        #     '__domain': ['&', ('model_id', '=', 462), ('method', '=', 'button_validate')],
        # },]

        method_dict_list = [dct for dct in method_duplicates if dct['__count'] > 1]
        injection_methods = [(env.ref(key).id, value[0]) for key, value, in EXTERNAL_IDS.items()]

        for method_dict in method_dict_list:

            model_id = method_dict['model_id'][0]
            method_name = method_dict['method']

            method_ids = env['printnode.action.method'].search(method_dict['__domain']).ids
            primary_method_id = method_ids[-1]

            if (model_id, method_name) in injection_methods:
                # Replace matched "action method" external-id to our from EXTERNAL_IDS
                model = env['ir.model'].browse(model_id)
                model_external_id = model.get_external_id()[model_id]
                method_external_id = EXTERNAL_IDS[model_external_id][1]
                primary_method_id = env.ref(method_external_id).id

            buttons_to_update = env['printnode.action.button'].with_context(**adds).search([
                ('model_id', '=', model_id),
                ('method_id', 'in', method_ids),
            ])
            buttons_to_update.write({'method_id': primary_method_id})

            method_ids.remove(primary_method_id)
            env['printnode.action.method'].browse(method_ids).unlink()
