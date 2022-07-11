# Copyright 2021 VentorTech OU
# License OPL-1.0 or later.

from odoo import fields, models, api


class PrintnodeMapActionServer(models.Model):
    _name = 'printnode.map.action.server'
    _description = 'Proxy model for ir.actions.server'

    active = fields.Boolean(
        string='Active',
        default=True,
    )
    name = fields.Char(
        string='Action Name',
        required=True,
        default='Print Attachments',
    )
    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Model',
        ondelete='cascade',
        required=True,
        domain=[('transient', '=', False)],
    )
    model_name = fields.Char(
        related='model_id.model',
        string='Model Name',
        readonly=True,
    )
    action_server_id = fields.Many2one(
        comodel_name='ir.actions.server',
        string='Action',
        ondelete='cascade',
    )

    _sql_constraints = [
        (
            'model_id_uniq',
            'unique (model_id)',
            'An attachment wizard exists for the current model!',
        ),
    ]

    @api.model
    def create(self, vals):
        res = super(PrintnodeMapActionServer, self).create(vals)
        action_server = self.env['ir.actions.server'].sudo().create({
            'state': 'code',
            'name': res.name,
            'binding_type': 'action',
            'model_id': res.model_id.id,
            'binding_model_id': res.model_id.id,
            'code': 'action = record.run_printnode_universal_wizard()',
        })
        res.write({'action_server_id': action_server.id})
        return res

    def write(self, vals):
        res = super(PrintnodeMapActionServer, self).write(vals)
        for rec in self:
            rec.action_server_id.sudo().write({
                'name': rec.name,
                'binding_model_id': rec.active and rec.model_id.id,
            })
        return res

    def unlink(self):
        action_servers = self.mapped('action_server_id')
        res = super(PrintnodeMapActionServer, self).unlink()
        action_servers.sudo().unlink()
        return res
