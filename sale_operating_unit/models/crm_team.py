# © 2019 ForgeFlow S.L.
# - Jordi Ballester Alomar
# © 2019 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import SUPERUSER_ID, _, api, models
from odoo.exceptions import ValidationError


class CrmTeam(models.Model):
    _inherit = "crm.team"

    @api.constrains("operating_unit_id")
    def _check_sales_order_operating_unit(self):
        for rec in self:
            orders = (
                self.with_user(SUPERUSER_ID)
                .env["sale.order"]
                .search(
                    [
                        ("team_id", "=", rec.id),
                        ("operating_unit_id", "!=", rec.operating_unit_id.id),
                    ]
                )
            )
            if orders:
                raise ValidationError(
                    _(
                        "Configuration error. It is not "
                        "possible to change this "
                        "team. There are sale orders "
                        "referencing it in other operating "
                        "units"
                    )
                )

    def _get_default_team_id(self, user_id=None, domain=None):
        # MAP CHANGE
        # Modify as there is always 1 sales team per group
        user_id = user_id or self.env.uid
        # Avoid searching on member_ids (+1 query) when we may have the user salesteam already in cache.
        team = self.env['crm.team'].search([
            ('company_id', 'in', [False, self.env.company.id]),
            ('operating_unit_id', 'in', [False, self.env.user.default_operating_unit_id.id]),
        ], limit=1)
        if not team and 'default_team_id' in self.env.context:
            team = self.env['crm.team'].browse(self.env.context.get('default_team_id'))
        return team or self.env['crm.team'].search(domain or [], limit=1)
