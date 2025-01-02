# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # 价格变更记录
    price_change_ids = fields.One2many('product.price.change', 'product_id', string='价格变更记录')


class ProductPriceChange(models.Model):
    _name = 'product.price.change'
    _description = '价格变更'

    name = fields.Many2one('res.supplier', string='供应商')
    # 产品
    product_id = fields.Many2one('product.product', string='产品')
    # 价格表
    price_id = fields.Many2one('product.price', string='价格表')
    # 变更类型
    change_type = fields.Selection([('add', '新增'), ('update', '更新'), ('delete', '删除')], string='变更类型')
    # 原价格
    old_price = fields.Float(string='原价格')
    # 新价格
    new_price = fields.Float(string='新价格')