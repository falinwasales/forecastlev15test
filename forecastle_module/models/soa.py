# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date
from num2words import num2words


class FceSoa(models.Model):
    _name = 'fce.soa'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def name_get(self):
        res = []
        for commission in self:
            res.append((commission.id, "%s/%s/%s" % (commission.principal_id.name, commission.date_from, commission.date_to)))
        return res

    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(string='Company Currency', readonly=True,
        related='company_id.currency_id')
    system_currency_id = fields.Many2one('res.currency', string="System Currency", compute="_get_system_currency")
    principal_id = fields.Many2one(
        'res.partner', domain="[('is_principal', '=', True)]",
        string="Principal", required=True)
    soa_line_ids = fields.Many2many('account.move.line', string="SOA Line")
    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)
    ap_difference = fields.Float(string="Balance", compute="_get_ap_difference")
    balance_soa_currency = fields.Float(string="Balance SOA Rates", compute="_get_balance_soa_currency")
    balance_system_currency = fields.Float(string="Balance System Rates", compute="_get_difference_system_rates")
    soa_difference_amount = fields.Float(string="Difference", compute="_get_difference_system_rates")
    move_id = fields.Many2one('account.move', string="SOA Journal", readonly=True)
    difference_move_id = fields.Many2one('account.move', string="Journal Difference", readonly=True)
    invoice_id = fields.Many2one('account.move', string="Settlement", readonly=True)
    payment_id = fields.Many2one('account.payment', string="Payment", readonly=True)
    move_line_id = fields.Many2one('account.move.line', string="Journal Item Difference", compute="_get_difference_line")
    soa_date = fields.Date(string='SOA Date', readonly=True)
    soa_currency_id = fields.Many2one('res.currency', string='SOA Currency', help="Currency For SOA")
    # container_number = fields.Many2one(string='Container Number', related='company_id.currency_id')

    # soa_value = fields.Float(string='SOA Value')

    @api.onchange('date_to', 'soa_currency_id')
    def _set_balance_soa_currency_on_move_line(self):
        for line in self.soa_line_ids:
            if self.soa_currency_id != line.company_currency_id and line.fal_invoice_mode not in ['commission', 'vendor_bill_c2c']:
                amount_total = line.company_currency_id._convert(
                    line.balance,
                    self.soa_currency_id,
                    line.company_id,
                    self.date_to or fields.Date.today()
                )
                line.balance_soa_currency = amount_total
            else:
                line.balance_soa_currency = line.amount_currency

    def _get_system_currency(self):
        for soa in self:
            soa.system_currency_id = self.env.ref('base.USD').id

    @api.depends('balance_soa_currency', 'balance_system_currency')
    def _get_difference_system_rates(self):
        for soa in self:
            soa.soa_difference_amount = abs(soa.balance_system_currency) - abs(soa.balance_soa_currency)

    @api.depends('move_id')
    def _get_difference_line(self):
        for soa in self:
            soa.move_line_id = soa.move_id.line_ids.filtered(lambda a: a.difference_line).id

    @api.depends('ap_difference', 'soa_currency_id')
    def _get_balance_soa_currency(self):
        for soa in self:
            soa.balance_soa_currency = sum(line.balance_soa_currency for line in soa.soa_line_ids.filtered(lambda a: not a.fce_exclude))
            # if soa.soa_currency_id != self.env.company.currency_id:
            #     amount_total = self.env.company.currency_id._convert(
            #         soa.ap_difference,
            #         soa.soa_currency_id,
            #         self.env.company,
            #         soa.date_to or fields.Date.today()
            #     )
            #     soa.balance_soa_currency = amount_total
            # else:
            #     soa.balance_soa_currency = soa.ap_difference

    @api.depends('soa_line_ids', 'soa_currency_id')
    def _get_ap_difference(self):
        for soa in self:
            soa.ap_difference = sum(line.balance for line in soa.soa_line_ids.filtered(lambda a: not a.fce_exclude))
            soa.balance_system_currency = sum(line.amount_currency for line in soa.soa_line_ids.filtered(lambda a: not a.fce_exclude))

    @api.onchange('principal_id', 'date_from', 'date_to')
    def _onchange_principal_date(self):
        if self.principal_id and self.date_to:
            lines = self.env['account.move.line'].search([
                ('partner_id', '=', self.principal_id.id),
                ('move_id.state', '=', 'posted'),
                # ('move_id.soa_date', '>=', self.date_from),
                ('move_id.soa_date', '<=', self.date_to),
                ('account_id.internal_type', 'in', ('receivable', 'payable')),
                ('account_id.is_contra_account', '=', True),
                ('reconciled', '=', False),
            ])

            self.soa_line_ids = lines
        else:
            self.soa_line_ids = False

    def _create_invoice(self):
        product = self.env['product.product'].search([('product_tmpl_id.is_interim_product', '=', True)], limit=1)
        if not product:
            raise UserError(_('Please Set Interim Product'))

        vals = {
            'partner_id': self.principal_id.id,
            'currency_id': self.soa_currency_id.id,
            'move_type': 'out_invoice' if self.balance_soa_currency > 0 else 'in_invoice',
            'invoice_line_ids': [(0, 0, {
                'product_id': product.id,
                'price_unit': abs(self.balance_soa_currency)
            })],
        }

        invoice = self.env['account.move'].create(vals)
        invoice.line_ids.filtered(lambda a: a.account_id.internal_type in ['receivable', 'payable']).write({
            'account_id': self.principal_id.property_principal_account_receivable_id.id if self.balance_soa_currency > 0 else self.principal_id.property_principal_account_payable_id.id
        })
        self.invoice_id = invoice.id

    def _create_journal_difference(self):
        if self.soa_difference_amount != 0.0:
            if not self.company_id.soa_gain_account_id.id:
                raise UserError(_('Please Set account Gain Forex in company'))

            soa_difference_amount = self.system_currency_id._convert(
                self.soa_difference_amount,
                self.company_currency_id,
                self.company_id,
                self.date_to or fields.Date.today()
            )
            vals = {
                'partner_id': self.principal_id.id,
                'move_type': 'entry',
                'line_ids': [(0, 0, {
                    'partner_id': self.principal_id.id,
                    'account_id': self.company_id.soa_gain_account_id.id,
                    'debit': soa_difference_amount if soa_difference_amount > 0 else 0,
                    'credit': -soa_difference_amount if soa_difference_amount < 0 else 0,
                }), (0, 0, {
                    'partner_id': self.principal_id.id,
                    'account_id': self.company_id.soa_gain_account_id.id,
                    'credit': soa_difference_amount if soa_difference_amount > 0 else 0,
                    'debit': -soa_difference_amount if soa_difference_amount < 0 else 0,
                })],
            }
            move = self.env['account.move'].create(vals)
            self.difference_move_id = move.id

    def open_soa_wizard(self, context=None):
        view = self.env.ref('forecastle_module.fal_view_soa_wizard')

        # for record in self:
            # for line in record.soa_line_ids.filtered(lambda x: x.fce_exclude == True):
        line_id = self.env.context.get('active_id',False)

        return {
            'name': _('SOA Wizard'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'fce.soa.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': {'soa_line_ids_wizard': self.env.context.get('soa_line_ids')},
        }

    def action_view_journal_item(self):
        move_ids = []
        for mv in self.soa_line_ids:
            move_ids.append(mv.move_id.id)

        return {
            'name': _('Journal Items'),
            'res_model': 'account.move.line',
            'view_mode': 'tree,form',
            'domain': [('move_id', 'in', move_ids)],
            'target': 'current',
            'views': [(self.env.ref('account.view_move_line_tree').id, 'tree'), (self.env.ref('account.view_move_line_form').id, 'form')],
            'context': {'search_default_group_by_move': 1},
            'type': 'ir.actions.act_window',
        }

    def _create_journal_entries(self):
        for soa in self:
            vals = {
                'partner_id': soa.principal_id.id,
                'move_type': 'entry',
                'line_ids': [],
            }
            created_move_lines = []
            for line in soa.soa_line_ids.filtered(lambda a: not a.fce_exclude):
                created_move_lines.append(line.id)
                line.soa_id = soa.id
                line_vals = {
                    'partner_id': line.partner_id.id,
                    'name': line.name,
                    'account_id': line.account_id.id,
                    'debit': line.credit,
                    'credit': line.debit,
                }
                vals['line_ids'].append((0, 0, line_vals))

            if vals['line_ids']:
                conterpart_line_vals = {
                    'partner_id': soa.principal_id.id,
                    'account_id': soa.principal_id.property_principal_account_interim_ar.id if soa.ap_difference > 0 else soa.principal_id.property_principal_account_interim_ap.id,
                    'debit': soa.ap_difference if soa.ap_difference > 0 else 0,
                    'credit': -soa.ap_difference if soa.ap_difference < 0 else 0,
                }
                vals['line_ids'].append((0, 0, conterpart_line_vals))

                move = self.env['account.move'].create(vals)
                move.action_post()

                # Auto Reconcile
                # Don't forget to filter out the counterpart account
                move_line_ids = soa.soa_line_ids.filtered(lambda a: not a.fce_exclude)
                move_line_ids |= move.line_ids.filtered(lambda a: a.account_id.internal_type in ['receivable', 'payable'] and a.account_id.id not in [soa.principal_id.property_principal_account_interim_ar.id, soa.principal_id.property_principal_account_interim_ap.id])

                move_line_ids.filtered(lambda a: a.account_id.internal_type == 'payable').reconcile()
                move_line_ids.filtered(lambda a: a.account_id.internal_type == 'receivable').reconcile()

                soa._create_invoice()
                soa._create_journal_difference()
                soa.move_id = move.id
                soa.soa_date = date.today()
                
            soa.soa_line_ids.write({'fce_exclude': False})
            soa.soa_line_ids = [(6, 0, created_move_lines)]


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    fce_exclude = fields.Boolean(string="Exclude")
    difference_line = fields.Boolean(string="Difference Line")
    soa_id = fields.Many2one('fce.soa', string="SOA")
    balance_soa_currency = fields.Float(string="Balance SOA Currency")
    sale_source_id = fields.Many2one(related='move_id.fal_sale_source_id', string="Sales Source")
    voyeg_id = fields.Many2one(related='sale_source_id.voyage_id', string="Voyage Id")
    vessel_id = fields.Many2one(related='sale_source_id.re_vessel_id', string="Vessel Id")
    feeder_vessel_id = fields.Char(related='sale_source_id.voyage_id.vessel_id.vessel_full_name', string="Feeder Vessel")
    mother_vessel_id = fields.Char(string="Mother Vessel", compute='_mother_vessel')
    no_bl = fields.Char(related='sale_source_id.bl_number', string="BL Number", copy=False,)
    container_number = fields.Many2many('stock.production.lot', string='Container Number', compute='_container_number')
     # related='sale_source_id.cro_ids.container_number_id'

    @api.depends('sale_source_id')
    def _container_number(self):
        for move_line in self:
            if move_line.sale_source_id:
                container = []
                for co in move_line.sale_source_id.cro_ids:
                    container += co.container_number_id.ids
                move_line.container_number = container
            else:
                move_line.container_number = False

    @api.depends('sale_source_id')
    def _mother_vessel(self):
        for move_line in self:
            if move_line.sale_source_id:
                vessel = ''
                for line in move_line.sale_source_id.connecting_vessel_id:
                    vessel = line.vessel_id.vessel_full_name
                move_line.mother_vessel_id = vessel
            else:
                move_line.mother_vessel_id = False


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def get_amount_to_text(self, total_receipt):
        return num2words(total_receipt)
