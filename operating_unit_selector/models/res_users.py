from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import partition, collections, lazy_property


class ResUsers(models.Model):
    _inherit = 'res.users'

    def sudo_write(self, vals):
        admin = self.env.ref('base.user_admin')
        self.with_user(admin).write(vals)

    def write(self, vals):
        result = super(ResUsers, self).write(vals)
        self.env['ir.model.access'].call_cache_clearing_methods()
        self.env['ir.rule'].clear_caches()
        return result

    @api.model_create_multi
    def create(self, vals_list):
        users = super(ResUsers, self).create(vals_list)
        self.env['ir.model.access'].call_cache_clearing_methods()
        self.env['ir.rule'].clear_caches()
        return users
