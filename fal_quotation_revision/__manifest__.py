# encoding: utf-8
# Part of Odoo - CLuedoo Edition. Ask Falinwa / CLuedoo representative for full copyright And licensing details.
{
    "name": "Quotation Revision",
    "version": "14.0.1.0.0",
    'license': 'OPL-1',
    'summary': 'Revised Quotation History',
    'sequence': 20,
    'category': 'Sales',
    'author': 'CLuedoo',
    'website': 'https://www.cluedoo.com',
    'support': 'cluedoo@falinwa.com',
    "description": """
Revised Quotation History
=========================

Generate history of revised quotation. User can click a Make Revise
Quotation button when they are in the SO Sent state. next this module
will generate history of revised Quotations with a versioning with
format (SOnum) v1, (SOnum) v2, etc.
    """,
    'depends': [
        'fal_sale_additional_info'
    ],
    'init_xml': [],
    'data': [
        'views/sale_order_views.xml',
    ],
    'images': [
        'static/description/quot_revise_screenshot.png'
    ],
    'demo': [],
    'css': [],
    'js': [],
    'qweb': [],
    'price': 360.00,
    'currency': 'EUR',
    'installable': True,
    'active': False,
    'application': False,
    'auto_install': False,
    'post_init_hook': '',
}
