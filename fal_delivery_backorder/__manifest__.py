# encoding: utf-8
# Part of Odoo - CLuedoo Edition. Ask Falinwa / CLuedoo representative for full copyright And licensing details.
{
    'name': "Delivery Backorder",
    'version': '14.0.1.0.0',
    'license': 'OPL-1',
    'summary': "Module to add backorder button in confirmed delivery",
    # 'sequence': 17,
    'category': 'Inventory',
    'author': "CLuedoo",
    'website': "https://www.cluedoo.com",
    'support': 'cluedoo@falinwa.com',
    'description': """

Delivery Backorder.
===============================

Module to add backorder at delivery.
    """,
    'depends': [
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'wizard/fal_stock_backorder_wizard_views.xml',
    ],
    'images': [
        # 'static/description/icon.png'
    ],
    'demo': [
    ],
    # 'price': 360.00,
    'currency': 'EUR',
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
