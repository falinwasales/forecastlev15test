from odoo import models


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ['purchase.order', 'printnode.scenario.mixin']

    def button_approve(self):
        super(PurchaseOrder, self).button_approve()

        self.print_scenarios(action='print_document_on_purchase_order')
        self.print_scenarios(action='print_picking_document_after_po_confirmation')

    def _scenario_print_picking_document_after_po_confirmation(
        self, report_id, printer_id, number_of_copies=1, **kwargs
    ):
        """
        Print picking document after PO confirmation
        """
        print_options = kwargs.get('options', {})

        # Print picking

        picking_ids = self.picking_ids.filtered(
            lambda p: p.picking_type_id == self.picking_type_id.warehouse_id.in_type_id)

        printer_id.printnode_print(
            report_id,
            picking_ids,
            copies=number_of_copies,
            options=print_options,
        )
