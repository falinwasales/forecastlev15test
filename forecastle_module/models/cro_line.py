# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import email_split
import datetime
import uuid
import logging

_logger = logging.getLogger(__name__)
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class fce_cro(models.Model):
    _name = 'fce.cro.line'
    _description = "Container Realease Order Line"

    list_of_container = fields.Many2one('product.product', string="List Of Container")
    cro_id = fields.Many2one('fce.cro', string="CRO ID")
    quantity = fields.Integer('Quantity')
