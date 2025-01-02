# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PackingType(models.Model):
    _name = 'packing.type'
    _description = '包装类型'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _sql_constraints = [('name_uniq', 'unique(name)', '包装类型名称必须唯一')]
    name = fields.Char(string='名称', required=True)
    code = fields.Char(string='编码')
    note = fields.Text(string='备注')
    # 长
    length = fields.Float(string='长')
    # 宽
    width = fields.Float(string='宽')
    # 高
    height = fields.Float(string='高')
    # 毛重
    gross_weight = fields.Float(string='毛重')
    # 净重
    net_weight = fields.Float(string='净重')
    # 装箱数量
    packing_qty = fields.Float(string='装箱数量')