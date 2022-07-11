# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Invoice Additional Info",
    "version": "14.0.1.0.0",
    'license': 'OPL-1',
    'summary': 'Invoice : Contact, Attachment, Archive',
    'category': 'Accounting',
    'author': 'CLuedoo',
    'website': "https://www.cluedoo.com",
    'support': 'cluedoo@falinwa.com',
    "description": """
        Invoice : Contact, Attachment, Archive
        ==============================================

        Module to add additional info in invoice customer / supplier
    """,
    "depends": ['account'],
    'data': [
        'views/invoice_view.xml',
        'views/company_view.xml',
        'views/account_analytic_view.xml',
        'report/invoice_report.xml',
    ],
    'images': [
        'static/description/invoice_screenshot.png'
    ],
    'demo': [
    ],
    'price': 180.00,
    'currency': 'EUR',
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
