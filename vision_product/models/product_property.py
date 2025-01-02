# -*- coding: utf-8 -*-

from odoo import models, fields, api


class VisionProductProperty(models.Model):
    _name = 'vision.product.property'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'vision Product Property'

    # 名称禁止重复
    # _sql_constraints = [('name_uniq', 'unique(name)', '名称禁止重复!')]

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        res = super(VisionProductProperty, self).copy({'name': self.name + '(复制)'})
        return res

    name = fields.Char(string='名称', required=True)
    # 产品类别
    category_id = fields.Many2one('product.category', string='类别', required=True)
    description = fields.Text(string='描述')
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
    property_line_ids = fields.One2many('vision.product.property.line', 'property_id', string='属性明细行', copy=True)

    def property_copy(self):
        # 复制创建一行相同属性
        self.copy()


# 属性明细行
class VisionProductPropertyLine(models.Model):
    _name = 'vision.product.property.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'vision Product Property Line'

    property_id = fields.Many2one('vision.product.property', string='属性')
    name = fields.Char(string='值', required=True)
    # 序号
    sequence = fields.Integer(string='序号')
    # 编码
    code = fields.Char(string='编码')
    # 属性间隔符
    sep_value = fields.Char(string='间隔符', default=',')
    # 产品类别
    # product_category_id = fields.Many2many('product.category', 'product_category_id', string='产品类别')





