# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockQuantity(models.Model):
    _name = 'stock.quantity'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '库存现有量查询表'

    name = fields.Char(string='名称', copy=False, index=True, default=lambda self: _('New'))
    product_id = fields.Many2one('product.product', string='产品')
    category_id = fields.Many2one('product.category', string='类别', related='product_id.category_id')
    # 库存单位
    product_uom_id = fields.Many2one('product.uom', string='单位', related='product_id.uom_id')
    barcode = fields.Char(string='条码', related='product_id.barcode')
    model = fields.Char(string='型号', related='product_id.model')
    location_id = fields.Many2one('stock.location', string='位置')
    quantity = fields.Float(string='数量')