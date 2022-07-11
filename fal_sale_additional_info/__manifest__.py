# -*- coding: utf-8 -*-
{
    'name': "Sales order Additional Info.",
    'version': '14.0.1.0.0',
    'license': 'OPL-1',
    'summary': "Sales order contact, attachment, archive.",
    'sequence': 20,
    'category': 'Sales',
    'author': "CLuedoo",
    'website': "https://www.cluedoo.com",
    'support': 'cluedoo@falinwa.com',
    'description': """
        Sales order: contact, attachment, archive.
        ===============================================================

        On Sales Order, we add info for Contact Person, Attachment and feature to Archive it
    """,
    'depends': ['sale_management', 'fal_invoice_additional_info'],
    'data': [
        'views/sale_view.xml',
        'views/sale_order_line_view.xml',
        'data/fal_multi_confirm.xml',
    ],
    'images': [
        'static/description/sale_order_screenshot.png'
    ],
    'demo': [
    ],
    'price': 360.00,
    'currency': 'EUR',
    'application': False,
}
