# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split
import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class fce_cro(models.Model):
    _name = 'fce.cro'
    _description = "Container Information"

    name = fields.Char("Name", compute="_get_name", store=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    sequence = fields.Integer("Sequence")
    sale_order_id = fields.Many2one('sale.order', 'Sale Order')
    sale_line_id = fields.Many2one('sale.order.line', 'Sale Order Line')
    container_type_id = fields.Many2one('product.product', 'Container Type')
    commodity = fields.Many2many('fce.commodity', string='Commodity')
    commodity_type = fields.Selection([
        ('dg', 'Dangerous Good'),
        ('standard', 'Standard')], string="Cargo Type", default='standard')
    container_categ = fields.Selection([
        ('soc', 'SOC'),
        ('coc', 'COC')], string="Cargo Type", default='coc')
    imdg_class = fields.Char("IMDG Class")
    ems_number = fields.Char("EMS Number")
    un_number = fields.Char("UN Number")
    set_temp = fields.Char("Temperature")
    length = fields.Char("Length")
    height = fields.Char("Height")
    width = fields.Char("Width")
    pg_class = fields.Char("PG Class")
    total_outer_dimension = fields.Char("Total Outer Dimension")
    hs_code = fields.Many2many('fce.hs.code', string='HS Code')
    container_number_id = fields.Many2one('stock.production.lot', string="Container No.")
    seal_number = fields.Many2one('fce.seal.number', string="Seal Number.")
    code_sequence = fields.Char("Code Sequence")
    # measure_code = fields.Char("Measure Code", compute='_meusercode')
    # gross_code = fields.Char("Gross Code", compute='_grosscode')
    gross = fields.Char('Gross Weight')
    nett = fields.Char('Net Weight')
    measure = fields.Char('Measure')
    gross_num = fields.Float('Gross Weight', compute='_get_gross_nett_meas')
    total_gross_num = fields.Float('Gross Weight', compute='_get_gross_nett_meas')
    nett_num = fields.Float('Net Weight', compute='_get_gross_nett_meas')
    measure_num = fields.Float('Measure', compute='_get_gross_nett_meas')

    @api.depends('gross', 'nett', 'measure')
    def _get_gross_nett_meas(self):
        for cro in self:
            cro.gross_num = 0.0
            cro.nett_num = 0.0
            cro.measure_num = 0.0
            if cro.gross:
                cro.gross_num = float(cro.gross)
                cro.total_gross_num += float(cro.gross)
            if cro.nett:
                cro.nett_num = float(cro.nett)
            if cro.measure:
                cro.measure_num = float(cro.measure)


    @api.depends('sequence', 'container_type_id')
    def _get_name(self):
        for cro in self:
            cro.name = "#%s %s" % (cro.sequence or '0', cro.container_type_id.name or '-')


class fce_commodity(models.Model):
    _name = 'fce.commodity'
    _description = "Commodity"

    name = fields.Char("Name")


class fce_seal_number(models.Model):
    _name = 'fce.seal.number'
    _description = "Seal Number"

    name = fields.Char("Name")
    cro_ids = fields.One2many('fce.cro', 'seal_number', string="List of CRO Using this Seal Number")

    @api.constrains('cro_ids')
    def constrains_used_one(self):
        for seal in self:
            if len(seal.cro_ids.ids) > 1:
                raise ValidationError(_("Seal Number have been Used."))

    _sql_constraints = [('unique_code', 'unique (name)', 'Seal Number must be unique!!')]


class ImportContainerInfo(models.Model):
    _name = 'import.container.info'
    _description = 'Container Info Import'

    def _get_currency_id(self):
        return self.env.ref('base.USD').id

    product_id = fields.Many2one('product.product', string="Container Product", domain=[('is_container', '=', True)])
    quantity = fields.Integer(string="Qty", default=1, readonly=1)
    ofr = fields.Float(string="OFR")
    con_deposit = fields.Float(string="Container Deposit", related='size.deposit_price', store=True)
    no_container = fields.Char('Nomor Container')
    no_container_id = fields.Many2one('stock.production.lot', string="No Container")
    ukuran_container = fields.Char('Ukuran Kontainer')
    tipe_container = fields.Char('Tipe Kontainer')
    container_type = fields.Selection(related="product_id.container_type", string="Tipe Kontainer")
    jenis_container = fields.Char('Jenis Kontainer')
    nomor_segel = fields.Char('Nomor segel')
    status_container = fields.Char('Status Kontainer')

    size = fields.Many2one('product.category', string="Size", related='product_id.categ_id')
    date_of_arrival = fields.Date(string="Discharge Date")
    free_time = fields.Selection([('day7', '7'), ('day14', '14'), ('day21', '21')], string="Free Time", default='day7')
    last_date = fields.Date(string="Last Date", compute='_compute_detention_date', store=True)
    request_extend_do = fields.Date(string="Request Extend DO")
    detention_days = fields.Float(string="Detention Days", compute='_compute_detention_date', store=True)
    non_slab = fields.Float(string="Non Slab", compute='_compute_formula', store=True)
    slab1 = fields.Float(string="Slab 1", compute='_compute_formula', store=True)
    slab2 = fields.Float(string="Slab 2", compute='_compute_formula', store=True)
    slab3 = fields.Float(string="Slab 3", compute='_compute_formula', store=True)
    slab4 = fields.Float(string="Slab 4", compute='_compute_formula', store=True)
    total_detention_deposit = fields.Float(string="Total Detention Deposit", compute='_compute_total_detention', store=True)
    actual_gate = fields.Date(string="Actual Gate in Depo", store=True)
    total_days = fields.Float(string="Total Days", compute='_compute_detention_date', store=True)
    total_detention_days = fields.Float(string="Total Detention Days", compute='_compute_detention_date', store=True)
    actual_detention_charge = fields.Float(string="Actual Detention Charge", compute='_compute_formula', store=True)
    refund_detention = fields.Float(string="Refund Detention", compute='_compute_refund_detention', store=True)

    currency_id = fields.Many2one('res.currency', default=_get_currency_id)
    sale_id = fields.Many2one('sale.order')
    detention_formula_id = fields.Many2one('detention.formula')

    def create(self, vals):
        res = super(ImportContainerInfo, self).create(vals)
        for con in res:
            con._onchange_container_size_type()
        return res

    @api.onchange('ukuran_container', 'tipe_container', 'no_container', 'imp_principal_id')
    def _onchange_container_size_type(self):
        if self.ukuran_container and self.tipe_container:
            tipe = []
            if self.tipe_container == '1':
                tipe = ['gp', 'hc']
            elif self.tipe_container == '2':
                tipe = ['tunne']
            elif self.tipe_container == '3':
                tipe = ['ot']
            elif self.tipe_container == '4':
                tipe = ['fr']
            elif self.tipe_container == '5':
                tipe = ['reefer', 'rh']
            elif self.tipe_container == '6':
                tipe = ['barge']
            elif self.tipe_container == '7':
                tipe = ['breakbulk']
            elif self.tipe_container == '8':
                tipe = ['tk']
            elif self.tipe_container == '99':
                tipe = ['other']

            product_id = self.env['product.product'].search([('container_size', '=', self.ukuran_container), ('container_type', 'in', tipe), ('is_container', '=', True)], limit=1)
            if product_id:
                detention = self.env['detention.formula'].search([
                    ('principal_id', '=', self.sale_id.imp_principal_id.id),
                    ('product_category', '=', product_id.categ_id.id)
                ])

                lot_id = self.env['stock.production.lot'].search([
                    ('name', '=', self.no_container),
                    ('product_id', '=', product_id.id)
                ])

                if not lot_id and self.no_container:
                    lot_id = self.env['stock.production.lot'].create({
                        'name': self.no_container,
                        'principal_id': self.sale_id.imp_principal_id.id,
                        'product_id': product_id.id,
                        'company_id': self.sale_id.company_id.id
                    })

                if not lot_id.principal_id:
                    lot_id.sudo().write({'principal_id': self.sale_id.imp_principal_id.id})

                self.no_container_id = lot_id.id
                self.product_id = product_id.id
                self.detention_formula_id = detention.id
            else:
                self.no_container_id = False
                self.product_id = False
                self.detention_formula_id = False

    @api.depends('slab1', 'slab2', 'slab3', 'slab4')
    def _compute_total_detention(self):
        for imp in self:
            imp.total_detention_deposit = imp.slab1 + imp.slab2 + imp.slab3 + imp.slab4

    @api.depends('date_of_arrival', 'free_time', 'request_extend_do', 'actual_gate')
    def _compute_detention_date(self):
        for con in self:
            days = 0
            if con.free_time == 'day7':
                days = 6
            elif con.free_time == 'day14':
                days = 13

            if days and con.date_of_arrival:
                last_date = con.date_of_arrival + relativedelta(days=days)
                con.last_date = last_date
                if con.request_extend_do:
                    date = con.request_extend_do - last_date
                    con.detention_days = date.days
                if con.actual_gate:
                    total_date = (con.actual_gate + relativedelta(days=1)) - con.date_of_arrival
                    con.total_days = total_date.days
                    detention_days = con.actual_gate - last_date
                    con.total_detention_days = detention_days.days

    @api.depends('total_detention_deposit', 'actual_detention_charge')
    def _compute_refund_detention(self):
        for con in self:
            con.refund_detention = con.total_detention_deposit - con.actual_detention_charge

    @api.depends('detention_formula_id', 'date_of_arrival', 'request_extend_do', 'actual_gate', 'free_time')
    def _compute_formula(self):
        for con in self:
            result = con.detention_formula_id._run_python_formula(con)
            if result:
                con.non_slab = result['non_slab']
                con.slab1 = result['slab1']
                con.slab2 = result['slab2']
                con.slab3 = result['slab3']
                con.slab4 = result['slab4']
                con.actual_detention_charge = result['actual_detention_charge']

    @api.onchange('detention_formula_id')
    def _onchange_detention_formula(self):
        if self.detention_formula_id:
            self.free_time = self.detention_formula_id.free_time
