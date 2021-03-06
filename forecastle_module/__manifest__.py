# encoding: utf-8
# Part of Odoo - CLuedoo Edition. Ask Falinwa / CLuedoo representative for full copyright And licensing details.
{
    "name": "Forecastle Module.",
    "version": "14.0.1.0.0",
    'license': 'OPL-1',
    'summary': 'Port Of Call',
    'sequence': 130,
    'category': 'New Project',
    'author': 'CLuedoo',
    'website': 'https://www.cluedoo.com',
    'support': 'cluedoo@falinwa.com',
    "description": """
        Schedule Management
        ======================================
    """,
    'depends': [
        'sale',
        'website',
        'base',
        'sale_management',
        'sale_product_set',
        'stock',
        'sale_purchase',
        # 'printnode_base',
        'fal_quotation_revision',
        'hr_expense',
        'sale_margin',
    ],
    'init_xml': [],
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/forecastle_group.xml',
        # JS Assets
        # 'views/assets.xml', // change call on web asset frontend// 
        'data/sale_product_menu.xml',
        # Portal
        'views/sale_forecastle_portal_templates.xml',
        # Report
        'report/forecastle_custom_header_footer_deposit.xml',
        'report/custom_header_footer_freight_manifest.xml',
        'report/forecastle_header_invoice.xml',
        'report/forecastle_header_telex_release.xml',
        'report/forecastle_official_receipt_container_deposit.xml',
        'report/forecastle_official_receipt_detention_deposit.xml',
        'report/forecastle_freight_manifest.xml',
        'report/forecastle_custom_header_footer.xml',
        'report/forecastle_header.xml',
        'report/forecastle_invoice.xml',
        'report/notice_of_arrival.xml',
        'report/forecastle_export_cargo_manifest.xml',
        'report/telex_release_notice.xml',
        'report/surat_pengantar_pengambilan_do.xml',
        'report/non_manipulation_certificate.xml',
        'report/free_time_certificate.xml',
        'report/shipping_instruction.xml',
        'report/forecastle_final_shipping.xml',
        'report/forecastle_official_receipt.xml',
        'report/forecastle_header_surat_tugas.xml',
        'report/forecastle_surat_tugas.xml',
        'report/forecastle_pre_alert_report.xml',
        'report/surat_pengantar_pengambilan_do_header.xml',
        'report/pro_forma_invoice.xml',
        'report/free_time_certificate_header.xml',
        'report/notice_of_arrival_header.xml',
        'report/telex_release_notice_header.xml',
        'report/non_manipulation_certificate_header.xml',
        'report/booking_confirmation.xml',
        'report/delivery_order.xml',
        'report/flat_file.xml',
        'report/manual_invoice.xml',
        'report/deposit_container.xml',
        'report/deposit_container_header.xml',
        'report/invoice_expense.xml',
        # Data
        'data/mail_data.xml',
        # Views
        'views/purchase_order_view.xml',
        'views/repair_view.xml',
        'views/commission_export_view.xml',
        'views/container_cost_view.xml',
        'views/detention_formula_view.xml',
        'views/soa_view.xml',
        'views/stock_production_lot.xml',
        'views/view_conves.xml',
        'views/view_cro.xml',
        'views/view_hs_code.xml',
        'views/view_port_code.xml',
        'views/view_port_of_call.xml',
        'views/view_product_line_set.xml',
        'views/view_product_pricelist.xml',
        'views/view_product_template.xml',
        'views/view_res_partner.xml',
        'views/account_move_view.xml',
        'views/view_sale_order.xml',
        'views/view_sale_order_import.xml',
        'views/view_slot_owner.xml',
        'views/view_terminal_code.xml',
        'views/view_vessel.xml',
        'views/view_voyage.xml',
        'views/view_reports.xml',
        'views/stock_picking.xml',
        'views/stock_location.xml',
        'views/view_res_currencies.xml',
        'views/group_code.xml',
        'views/view_kpbc.xml',
        'views/view_package_code.xml',
        'views/hr_expense_view.xml',
        'views/view_agent_code.xml',
        'views/view_seal_number.xml',
        # Menu
        'views/menu.xml',
        # Wizard
        'wizard/product_set_add_views.xml',
        'wizard/surat_tugas_view_wizard.xml',
        'wizard/soa_wizard_views.xml',
    ],
    'images': [
        'static/description/meeting_screenshot.png'
    ],
    'demo': [],
    'css': [],
    'js': [],
    'qweb': [],
    'price': 540.00,
    'currency': 'EUR',
    'installable': True,
    'active': False,
    'application': False,
    'auto_install': False,
    'post_init_hook': '',
    'assets': {
        'web.assets_frontend': [
            'forecastle_module/static/src/js/sale_portal_sidebar.js',
            'forecastle_module/static/src/js/content/website_root.js',
        ],
    },
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
