# Copyright 2021 VentorTech OU
# License OPL-1.0 or later.

from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        res = super(IrHttp, self).session_info()

        printnode_enabled = False
        if self.env.user.has_group("printnode_base.printnode_security_group_user") \
                and self.env.company.printnode_enabled and self.env.user.printnode_enabled:
            printnode_enabled = True

        res.update({
            'printnode_enabled': printnode_enabled
        })
        return res
