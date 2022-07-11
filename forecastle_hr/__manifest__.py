# encoding: utf-8
{
    "name": "Forecastle HR",
    "version": "14.0.1.0.0",
    'license': 'OPL-1',
    'summary': 'Improvement For HR module',
    'category': 'Human Resource',
    'author': 'Falinwa',
    'website': 'https://www.falinwa.com',
    'support': 'sales@falinwa.com',
    "description": """
    """,
    'depends': [
        'website_hr_recruitment',
        'contacts',
        'website_form_project',
        'odoo_whatsapp_integration',
    ],
    'init_xml': [],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'report/forecastle_offering_letter.xml',
        'views/hr_view.xml',
        'views/contact_view.xml',
        'views/contract_views.xml',
        'views/hr_applicant_view.xml',
        'views/website_hr_recruitment_templates.xml',
    ],
    'images': [

    ],
    'assets': {
        'web.assets_backend': [
            'forecastle_hr/static/src/js/basic_fields.js',
        ],
        'web.assets_frontend': [
            'forecastle_hr/static/src/snippets/s_website_form/image_specify.js',
            'forecastle_hr/static/src/js/easy-number-separator.js',
        ],
    },
    'demo': [],
    'css': [],
    'js': [],
    'qweb': [],
}
