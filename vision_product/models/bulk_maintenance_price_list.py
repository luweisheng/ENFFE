# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BulkMaintenancePrice(models.TransientModel):
    _name = 'bulk.maintenance.price'
    _description = '批量维护价格表'

    name = fields.Char(string='名称', default='批量维护价格表')
    # 批量维护价格表子表
    line_ids = fields.One2many('bulk.maintenance.price.line', 'maintenance_id', string='批量维护价格表子表')

    def update_price_list(self):
        for line in self.line_ids:
            origin_price_id = self.env['product.price'].search([
                ('name', '=', line.supplier_id.id),
                ('product_id', '=', line.product_id.id),
            ], limit=1)
            if origin_price_id:
                if origin_price_id.price != line.price:
                    origin_price_id.write({
                        'price': line.price
                    })
            else:
                price_id = self.env['product.price'].create({
                    'name': line.supplier_id.id,
                    'product_id': line.product_id.id,
                    'min_qty': line.min_qty,
                    'price': line.price,
                    'note': line.note,
                })
                line.bom_line_id.price_id = price_id.id
        return {'type': 'ir.actions.act_window_close'}


class BulkMaintenancePriceLine(models.TransientModel):
    _name = 'bulk.maintenance.price.line'
    _description = '批量维护价格表子表'

    name = fields.Char(string='名称', default='批量维护价格表子表')
    maintenance_id = fields.Many2one('bulk.maintenance.price', string='批量维护价格表')
    bom_line_id = fields.Many2one('mrp.bom.line', string='BOM明细')
    # 供应商
    supplier_id = fields.Many2one('res.supplier', string='供应商')
    # 产品
    product_id = fields.Many2one('product.product', string='产品', related='bom_line_id.product_id')
    # 类别
    category_id = fields.Many2one('product.category', string='类别', related='product_id.category_id')
    # 条码
    barcode = fields.Char(string='条码', related='product_id.barcode')
    # 型号
    model = fields.Char(string='型号', related='product_id.model')
    # 起订量
    min_qty = fields.Float(string='起订量', default=1)
    # 单价
    price = fields.Float(string='单价', default=1)
    note = fields.Text(string='备注')
