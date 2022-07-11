from odoo import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"
 
    fal_user_depo_id = fields.Many2one('res.partner', string="Depot", compute='_get_addres_warehouse', store=True)
    current_user = fields.Many2one('res.users', compute='_get_current_user')
    member_ids = fields.Many2many('res.users', string='Members', check_company=True, domain=[('share', '=', False)], compute='_get_team_member')

    # check user use or see depot
    def _get_team_member(self):
        users = self.env['res.users'].search([('depot_ids', 'in', self.fal_user_depo_id.ids)])
        self.member_ids = False
        if users:
            self.member_ids = [(6, 0, users.ids)]

    # check address or partner in warehouse
    @api.depends('warehouse_id')
    def _get_addres_warehouse(self):
        for picking_type in self:
            picking_type.fal_user_depo_id = False
            if picking_type.warehouse_id:
                picking_type.fal_user_depo_id = picking_type.warehouse_id.partner_id

    def _get_current_user(self):
        for rec in self:
            rec.current_user = self.env.user
        self.update({'current_user' : self.env.user.id})

    def _get_depo(self):
        for rec in self:
            rec.fal_user_depo_id = rec.current_user.fal_user_depo_id
        # self.update({'fal_user_depo_id' : rec.current_user.fal_user_depo_id})

class ResUsers(models.Model):
    _inherit = "res.users"

    depot_ids = fields.Many2many('res.partner', 'res_users_depot_rel', 'depot_id', string='Depot')
    fal_user_depo_id = fields.Many2one('res.partner', string="Depot")
    current_user = fields.Many2one('res.users', compute='_get_current_user')

    def _get_current_user(self):
        for rec in self:
            rec.current_user = self.env.user
        self.update({'current_user' : self.env.user.id})

class StockLocation(models.Model):
    _inherit = "stock.location"

    fal_user_depo_id = fields.Many2one('res.partner', string="Depot", compute='_get_depo')
    current_user = fields.Many2one('res.users', compute='_get_current_user')
    member_ids = fields.Many2many('res.users', string='Members', check_company=True, domain=[('share', '=', False)], compute='_get_team_member')

    # check user use or see depot
    def _get_team_member(self):
        users = self.env['res.users'].search([('depot_ids', 'in', self.depot_id.ids)])
        self.member_ids = False
        if users:
            self.member_ids = [(6, 0, users.ids)]

    def _get_current_user(self):
        for rec in self:
            rec.current_user = self.env.user
        self.update({'current_user' : self.env.user.id})

    def _get_depo(self):
        for rec in self:
            rec.fal_user_depo_id = rec.current_user.fal_user_depo_id
        # self.update({'fal_user_depo_id' : rec.current_user.fal_user_depo_id})


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    depot_id = fields.Many2one('res.partner', related='picking_type_id.fal_user_depo_id', store=True)
