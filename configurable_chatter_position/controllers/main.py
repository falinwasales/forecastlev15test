from odoo import http
from odoo.http import request


class ChatterPosition(http.Controller):
    @http.route(
        ["/configurable_chatter_position"],
        type="json",
    )
    def onchange_chatter_position(self, auth="user", **kw):
        """
            Endpoint to update (store) the chatter position chosen by the user
        """
        user = (
            request.env["res.users"].sudo().search([("id", "=", request.session.uid)])
        )
        if kw.get("chatter_position") == "right":
            user.context_chatter_position = "chatter_right"
        else:
            user.context_chatter_position = "chatter_bottom"
