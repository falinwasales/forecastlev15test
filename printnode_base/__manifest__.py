# Copyright 2019 VentorTech OU
# License OPL-1.0 or later.

{
    'name': 'Odoo Direct Print PRO',
    'summary': """
        Print any reports or shipping labels directly to any local,
        Wi-Fi or Bluetooth printer without downloading PDF or ZPL!
    """,
    'version': '14.0.1.9.3',
    'category': 'Tools',
    "images": ["static/description/images/image1.gif"],
    'author': 'VentorTech',
    'website': 'https://ventor.tech',
    'support': 'support@ventor.tech',
    'license': 'OPL-1',
    'live_test_url': 'https://odoo.ventor.tech/',
    'price': 199.00,
    'currency': 'EUR',
    'depends': [
        'web',
        'stock',
        'delivery',
        'sale',
        'purchase',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'reports/package_zpl_template.xml',
        'data/ir_actions.xml',
        'data/ir_crons.xml',
        'data/emails.xml',
        'data/printnode_actions.xml',
        'data/printnode_data.xml',
        'views/printnode_views.xml',
        # 'views/assets.xml',
        'wizard/printnode_report_abstract_wizard.xml',
        'wizard/product_label_multi_print.xml',
        'wizard/printnode_attach_universal_wizard.xml',
    ],
    'qweb': [
        'views/printnode_status_menu.xml',
        'static/src/xml/*.xml',
    ],
    'installable': True,
    'application': True,
    "cloc_exclude": [
        "**/*"
    ]
}
