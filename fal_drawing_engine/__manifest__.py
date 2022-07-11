# encoding: utf-8
# Part of Odoo - CLuedoo Edition. Ask Falinwa / CLuedoo representative for full copyright And licensing details.
{
    'name': "Drawing Engine",
    'version': '15.0.1.0.0',
    'license': 'OPL-1',
    'summary': "Drawing Engine",
    'category': 'Tools',
    'author': "CLuedoo",
    'website': "https://www.cluedoo.com",
    'support': 'cluedoo@falinwa.com',
    'description': """
Drawing Engine
===============================================================

Module to have Drawing
    """,
    'depends': [
        'web'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/drawing_view.xml',
    ],
    'images': [
    ],
    'demo': [],
    'price': 0.00,
    'currency': 'EUR',
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
