# Copyright 2021 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import models


class Base(models.AbstractModel):
    _inherit = 'base'

    def run_printnode_universal_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Print Attachments Wizard',
            'res_model': 'printnode.attach.universal.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('printnode_base.printnode_attach_universal_wizard_form').id,
            'target': 'new',
            'context': self.env.context,
        }
