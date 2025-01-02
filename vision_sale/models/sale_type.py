# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleType(models.Model):
    _name = 'sale.type'
    _description = '销售类型'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _sql_constraints = [('name_uniq', 'unique(name)', '销售类型名称必须唯一')]
    name = fields.Char(string='名称', required=True)
    code = fields.Char(string='编码')
    note = fields.Text(string='备注')