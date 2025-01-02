# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockAllotBase(models.TransientModel):
    _name = 'stock.allot.base'
    _description = '库存调拨基础'

    name = fields.Char(string='名称')
    picking_type_id = fields.Many2one('stock.picking.type', string='单据类型')
    # 源位置
    location_id = fields.Many2one('stock.location',
                                  string='来源位置',
                                  domain=lambda self: [('id', 'in', self.picking_type_id.location_src_permit_ids.ids)])
    # 目标位置
    location_dest_id = fields.Many2one('stock.location',
                                       string='目标位置',
                                       domain=lambda self: [('id', 'in', self.picking_type_id.location_dest_permit_ids.ids)])
    # 数量
    product_qty = fields.Float(string='数量')
    # 备注
    note = fields.Char(string='备注')
    # 入库明细
    stock_line_ids = fields.One2many('stock.allot.base.line', 'stock_allot_id', string='调拨明细')

    @api.onchange('location_id')
    def _onchange_location_dest_id(self):
        self.stock_line_ids.location_id = self.location_id.id

    @api.onchange('location_dest_id')
    def _onchange_location_dest_id(self):
        self.stock_line_ids.location_dest_id = self.location_dest_id.id

    # 禁止源位置和目标位置相同
    @api.onchange('location_id', 'location_dest_id')
    def _onchange_location_src_dest_id(self):
        if self.location_id == self.location_dest_id:
            raise UserError(_('源位置和目标位置不能相同！'))

    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        # 数量禁止小于0
        if self.product_qty < 0:
            raise UserError(_('数量不能小于0！'))


class StockAllotBaseLine(models.TransientModel):
    _name = 'stock.allot.base.line'
    _description = '库存调拨基础明细'

    stock_allot_id = fields.Many2one('stock.allot.base', string='库存调拨')

    product_id = fields.Many2one('product.product', string='产品')
    # 类别
    category_id = fields.Many2one('product.category', string='类别', related='product_id.category_id')
    # 条码
    barcode = fields.Char(string='条码', related='product_id.barcode')
    # 型号
    model = fields.Char(string='型号', related='product_id.model')
    # 源位置
    location_id = fields.Many2one('stock.location', string='来源位置')
    # 目标位置
    location_dest_id = fields.Many2one('stock.location', string='目标位置')
    uom_id = fields.Many2one('product.uom', string='单位')
    done_qty = fields.Float(string='调拨数')
    product_qty = fields.Float(string='调拨数')
    origin = fields.Char(string='来源')
    sale_origin = fields.Char(string='销售来源')
    contract_no = fields.Char(string='合同号')
    # 备注
    note = fields.Text(string='备注')


class StockBaseFunction(models.AbstractModel):
    _name = 'stock.base.function'
    _description = '库存基础功能'

    # 更新现有量
    def update_stock_quantity(self, location_id, product_id, done_qty):
        stock_quantity = self.env['stock.quantity'].search([
            ('product_id', '=', product_id.id),
            ('location_id', '=', location_id.id)
        ], limit=1)
        # 采购单位转库存单位
        if product_id.uom_id.id != product_id.po_uom_id.id:
            done_qty = done_qty * product_id.uom_factor
        else:
            done_qty = done_qty
        if stock_quantity:
            new_quantity = stock_quantity.quantity + done_qty
            # 禁止负库存
            if location_id.location_type == 'internal' and new_quantity < 0:
                raise UserError(_('库存不足, 禁止负库存操作！'))
            stock_quantity.quantity = new_quantity
        else:
            self.env['stock.quantity'].create({
                'product_id': product_id.id,
                'location_id': location_id.id,
                'quantity': done_qty
            })