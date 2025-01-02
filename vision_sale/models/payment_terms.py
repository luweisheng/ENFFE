# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PaymentTerms(models.Model):
    _name = 'payment.terms'
    _description = '付款条款'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _sql_constraints = [('name_uniq', 'unique(name)', '付款条款名称必须唯一')]
    name = fields.Char(string='名称', required=True)
    code = fields.Char(string='编码')
    note = fields.Text(string='备注')
    days = fields.Integer(string='天数')
    discount = fields.Float(string='折扣(%)')