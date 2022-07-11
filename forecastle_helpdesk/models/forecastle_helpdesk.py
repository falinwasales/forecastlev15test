from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)

class HelpdeskTicket(models.Model):
    _inherit='helpdesk.ticket'

    fce_location = fields.Text(string='Location', required=True)    
    user_id = fields.Many2one(
        'res.users', string='Assigned to',
        domain=lambda self: [('groups_id', 'in', self.env.ref('helpdesk.group_helpdesk_user').id)])
    can_edit = fields.Boolean("Can Edit", compute='_compute_can_edit_type')
    description = fields.Text(string='Description', required=True) 
    fal_user_selection = fields.Selection([('customer','Customer'),('employee','Employee')], default='customer')
    fal_employee = fields.Many2one('res.partner', string="Employee")
    fal_employee_email = fields.Char(string="Employee Email")

    @api.constrains('description')
    def _check_description(self):
        if len(self.description) < 100:
            raise ValidationError('Minumum Character Must More Than 100 Character')

    @api.depends('user_id')
    def _compute_can_edit_type(self):
        for ticket in self:
            ticket.can_edit = self.env.user.id in self.env.ref('helpdesk.group_helpdesk_manager').users.ids

    @api.onchange("fal_user_selection")
    def onchange_employee_email(self):
        self.fal_employee = self.env.user.partner_id.id
        self.fal_employee_email = self.env.user.partner_id.email

    # @api.onchange('fal_user_selection')
    # def _onchange_user_selection(self):
    #     if self.fal_user_selection == 'employee':
    #         self.fal_employee = self.env.user.employee_ids.id
    #     else:
    #         self.fal_employee = False
