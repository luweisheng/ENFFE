# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockMove(models.Model):
    _name = 'stock.move'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '库存移动'

    name = fields.Char(string='名称', copy=False, index=True, default=lambda self: _('New'))
    picking_id = fields.Many2one('stock.picking', string='库存移动')
    # 单据类型
    picking_type_id = fields.Many2one('stock.picking.type', string='单据类型')
    # 源位置
    location_id = fields.Many2one('stock.location', string='源位置', required=True)
    # 目标位置
    location_dest_id = fields.Many2one('stock.location', string='目标位置', required=True)
    # 状态
    # state = fields.Selection([
    #     ('draft', '草稿'),
    #     ('wait', '代办'),
    #     ('done', '完成'),
    #     ('cancel', '取消')
    # ], string='状态', default='draft')
    state = fields.Selection([
        ('draft', '草稿'),
        ('done', '完成'),
        ('cancel', '取消')
    ], string='状态', default='draft')
    # 供应商
    supplier_id = fields.Many2one('res.supplier', string='供应商')
    # 客户
    corporation_id = fields.Many2one('res.corporation', string='客户')

    # 销售单
    sale_order_id = fields.Many2one('sale.order', string='销售单')
    sale_origin = fields.Char(string='销售来源')
    origin = fields.Char(string='源单据')
    sale_price = fields.Float(string='销售价格')
    purchase_price = fields.Float(string='采购价格')
    # 合同号
    contract_no = fields.Char(string='合同号')
    # 单据日期
    done_date = fields.Datetime(string='单据日期')
    # 产品
    product_id = fields.Many2one('product.product', string='产品', required=True)
    # 类别
    category_id = fields.Many2one('product.category', string='类别', related='product_id.category_id')
    # 条码
    barcode = fields.Char(string='条码', related='product_id.barcode')
    # 型号
    model = fields.Char(string='型号', related='product_id.model')
    # 图号
    drawing_number = fields.Char(string='图号', related='product_id.drawing_number')
    # 单位
    product_uom_id = fields.Many2one('product.uom', string='单位')
    # 需求数
    product_uom_qty = fields.Float(string='需求数')
    product_qty = fields.Float(string='需求数')
    # 完成数
    done_qty = fields.Float(string='完成数')
    # 备注
    note = fields.Text(string='备注')
    purchase_id = fields.Many2one('purchase.order', string='采购单')
    sale_id = fields.Many2one('sale.order', string='销售单')
    production_id = fields.Many2one('mrp.production', string='生产单')
    purchase_line_id = fields.Many2one('purchase.order.line', string='采购明细')
    # 生产明细
    production_line_id = fields.Many2one('mrp.production.line', string='生产明细')
    sale_line_id = fields.Many2one('sale.order.line', string='销售明细')
    # 库存变化方式：增加、减少
    stock_change_type = fields.Selection([
        ('add', '增加'),
        ('reduce', '减少')
    ], string='库存变化方式', default='add')


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    stock_move_ids = fields.One2many('stock.move', 'purchase_line_id', string='库存移动')

