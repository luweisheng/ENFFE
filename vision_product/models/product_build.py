# -*- coding: utf-8 -*-

from odoo import models, fields, api


# 属性明细行
class VisionProductBuilderLine(models.Model):
    _name = 'vision.product.builder.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '产品属性明细行'

    # 序号
    sequence = fields.Integer(string='序号')
    category_id = fields.Many2one('product.category', string='类别')
    # 属性
    property_id = fields.Many2one('vision.product.property', string='属性')
    # 向客户隐藏
    hide_from_customer = fields.Boolean(string='向客户隐藏')
    # 向供应商隐藏
    hide_from_supplier = fields.Boolean(string='向供应商隐藏')
    # 必填项
    required = fields.Boolean(string='必填项', default=True)
    # 参与编码
    participate_code = fields.Boolean(string='参与编码')
    # 显示名称
    show_name = fields.Boolean(string='显示名称')
    # 备注
    note = fields.Text(string='备注')
    # 编码
    # code = fields.Char(related='property_id.code', string='编码')
    # # 间隔符
    # sep_value = fields.Char(related='property_id.sep_value', string='间隔符')