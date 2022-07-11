from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    context_chatter_position = fields.Selection([
        ("chatter_bottom", "Bottom"),
        ("chatter_right", "Right")
    ],
        string="Chatter Position",
        default="chatter_right",
    )

    def __init__(self, pool, cr):
        """
            Override of __init__ to add access rights.
            Access rights are disabled by default, but allowed on some specific
            fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        super(ResUsers, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(["context_chatter_position"])
        # duplicate list to avoid modifying the original reference
        type(self).SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        type(self).SELF_READABLE_FIELDS.extend(["context_chatter_position"])
