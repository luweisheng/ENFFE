# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


# 价格表
class ProductPrice(models.Model):
    _name = 'product.price'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '价格表'

    # 价格禁止小于等于0, 起订量禁止小于等于0
    _sql_constraints = [('price_check', 'CHECK(price > 0)', '价格必须大于0'),
                        ('min_qty_check', 'CHECK(min_qty > 0)', '起订量必须大于0')]

    name = fields.Many2one('res.supplier', string='供应商', required=True)
    display_name = fields.Char(string='名称', store=True, compute='_compute_display_name')

    @api.depends('name', 'price')
    def _compute_display_name(self):
        for price in self:
            price.display_name = str(price.name.name) + ' - ' + str(price.price)
    # 产品
    product_id = fields.Many2one('product.product', string='产品', required=True)
    # 类别
    category_id = fields.Many2one('product.category', string='类别', related='product_id.category_id', store=True)
    # 条码
    barcode = fields.Char(string='条码', related='product_id.barcode', store=True)
    # 型号
    model = fields.Char(string='型号', related='product_id.model', store=True)
    # 图号
    drawing_number = fields.Char(string='图号', related='product_id.drawing_number', store=True)
    # 起订量
    min_qty = fields.Float(string='起订量', required=True, default=1)
    # 单价
    price = fields.Float(string='单价', required=True, default=1)
    note = fields.Text(string='备注')
    # 含税
    tax_included = fields.Boolean(string='含税')
    # 税率
    tax_rate = fields.Float(string='税率', default=0.13)
    # 含税单价
    tax_price = fields.Float(string='含税单价', compute='_compute_tax_price', store=True)
    # 交货提前期
    delivery_lead_time = fields.Integer(string='交货提前期', default=7)

    @api.depends('price', 'tax_rate')
    def _compute_tax_price(self):
        for price in self:
            price.tax_price = price.price * (1 + price.tax_rate)

    # 新增价格记录到对应产品的价格变更
    @api.model
    def create(self, vals):
        product_price = super(ProductPrice, self).create(vals)
        self.env['product.price.change'].create({
            'name': vals.get('name'),
            'product_id': vals.get('product_id'),
            'price_id': product_price.id,
            'change_type': 'add',
            'new_price': vals.get('price')
        })
        return product_price

    # 更新价格记录到对应产品的价格变更
    def write(self, vals):
        old_price = self.price
        res = super(ProductPrice, self).write(vals)
        if 'price' in vals:
            self.env['product.price.change'].create({
                'name': self.name.id,
                'product_id': self.product_id.id,
                'price_id': self.id,
                'change_type': 'update',
                'old_price': old_price,
                'new_price': vals.get('price')
            })
        return res

    # 删除价格记录到对应产品的价格变更
    def unlink(self):
        for price in self:
            self.env['product.price.change'].create({
                'name': price.name.id,
                'product_id': price.product_id.id,
                'price_id': price.id,
                'change_type': 'delete',
                'old_price': price.price
            })
        return super(ProductPrice, self).unlink()


