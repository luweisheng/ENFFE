# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockLocation(models.Model):
    _name = 'stock.location'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '库位'

    _sql_constraints = [('name_uniq', 'unique(name)', '库位名称必须唯一')]

    name = fields.Char(string='名称', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    code = fields.Char(string='代码', required=True)
    # 类型
    location_type = fields.Selection([
        ('partner', '供应商'),
        ('client', '客户'),
        ('internal', '实体仓'),
        ('virtual', '虚拟')
    ], string='类型', default='internal', required=True)

    # 禁止负库存
    forbid_negative_stock = fields.Boolean(string='禁止负库存')
