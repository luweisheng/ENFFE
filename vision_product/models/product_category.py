# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductCategory(models.Model):
    _name = 'product.category'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '产品类别'

    _sql_constraints = [('name_uniq', 'unique(name)', '名称禁止重复!')]

    name = fields.Char(string='名称', required=True, default='_New')
    # 类别编码
    code = fields.Char(string='编码', required=True)
    # 条码长度
    barcode_length = fields.Integer(string='条码长度', default=13)
    builder_line_ids = fields.One2many('vision.product.property', 'category_id', string='产品属性列表', copy=True)
    # 排序号
    sequence = fields.Integer(string='排序号')
    # 库存单位
    uom_id = fields.Many2one('product.uom', string='库存单位', required=True, track_visibility='always')
    # 采购单位
    po_uom_id = fields.Many2one('product.uom', string='采购单位', required=True, track_visibility='always')
    # 可销售
    sale_ok = fields.Boolean(string='可销售', default=True)
    # 可采购
    purchase_ok = fields.Boolean(string='可采购', default=True)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        res = super(ProductCategory, self).copy({'name': self.name + '(复制)'})
        return res

    product_ids = fields.One2many('product.product', 'category_id', string='产品列表')

