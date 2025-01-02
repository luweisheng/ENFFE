# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VisionAvailabilityQuery(models.TransientModel):
    _name = 'vision.availability.query'
    _description = '库存可用量查询表'

    name = fields.Char(string='名称', copy=False, index=True, default=lambda self: _('New'))
    product_id = fields.Many2one('product.product', string='产品')
    # 在手量
    quantity = fields.Float(string='在手量', readonly=True)
    quantity_line_ids = fields.One2many('vision.availability.query.line', 'query_id', string='现有量明细')
    # 采购在途
    purchase_in_transit = fields.Float(string='采购在途', readonly=True)
    purchase_in_transit_line_ids = fields.One2many('vision.purchase.availability.query.line', 'query_id', string='采购在途明细')
    # 销售在途
    sale_in_transit = fields.Float(string='销售在途', readonly=True)
    sale_in_transit_line_ids = fields.One2many('vision.sale.availability.query.line', 'query_id', string='销售在途明细')
    # 生产在途
    production_in_transit = fields.Float(string='生产在途', readonly=True)
    production_in_transit_line_ids = fields.One2many('vision.production.availability.query.line', 'query_id', string='生产在途明细')
    # 可用量
    availability = fields.Float(string='可用量', readonly=True)


class VisionAvailabilityQueryLine(models.TransientModel):
    _name = 'vision.availability.query.line'
    _description = '库存可用量查询表明细'

    query_id = fields.Many2one('vision.availability.query', string='查询表')

    location_id = fields.Many2one('stock.location', string='位置')
    quantity = fields.Float(string='数量')


class VisionPurchaseAvailabilityQueryLine(models.TransientModel):
    _name = 'vision.purchase.availability.query.line'
    _description = '库存可用量查询表明细'

    query_id = fields.Many2one('vision.availability.query', string='查询表')

    purchase_id = fields.Many2one('purchase.order', string='采购订单')
    quantity = fields.Float(string='数量')


class VisionSaleAvailabilityQueryLine(models.TransientModel):
    _name = 'vision.sale.availability.query.line'
    _description = '库存可用量查询表明细'

    query_id = fields.Many2one('vision.availability.query', string='查询表')

    sale_id = fields.Many2one('sale.order', string='销售订单')
    quantity = fields.Float(string='数量')


class VisionProductionAvailabilityQueryLine(models.TransientModel):
    _name = 'vision.production.availability.query.line'
    _description = '库存可用量查询表明细'

    query_id = fields.Many2one('vision.availability.query', string='查询表')

    production_id = fields.Many2one('mrp.production', string='生产订单')
    quantity = fields.Float(string='数量')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def action_open_availability_query_view(self):
        # 可用量 = 现有量 + 采购在途 - 销售在途 - 生产在途
        quantity_line_ids = []
        purchase_in_transit_line_ids = []
        sale_in_transit_line_ids = []
        production_in_transit_line_ids = []
        product_id = self.id
        quantity = 0
        purchase_in_transit = 0
        sale_in_transit = 0
        production_in_transit = 0
        for location in self.env['stock.quantity'].search_read([('product_id', '=', product_id), ('location_id.location_type', '=', 'internal')], ['location_id', 'quantity']):
            quantity = location['quantity']
            if quantity > 0:
                quantity_line_ids.append((0, 0, {
                    'location_id': location['location_id'][0],
                    'quantity': quantity
                }))
                quantity += quantity

        for purchase_line in self.env['purchase.order.line'].search_read([('product_id', '=', self.id), ('order_id.state', '=', 'done')], ['order_id', 'stock_qty_no']):
            quantity = purchase_line['stock_qty_no']
            if quantity > 0:
                purchase_in_transit_line_ids.append((0, 0, {
                    'purchase_id': purchase_line['order_id'][0],
                    'quantity': quantity
                }))
                purchase_in_transit += quantity

        for sale_line in self.env['sale.order.line'].search_read([('product_id', '=', self.id), ('order_id.state', '=', 'done')], ['order_id', 'product_uom_qty', 'qty_delivered']):
            quantity = sale_line['product_uom_qty'] - sale_line['qty_delivered']
            if quantity > 0:
                sale_in_transit_line_ids.append((0, 0, {
                    'sale_id': sale_line['order_id'][0],
                    'quantity': quantity
                }))
                sale_in_transit += quantity

        for production_line in self.env['mrp.production.line'].search_read([('product_id', '=', self.id)], ['production_id', 'product_qty', 'picking_qty']):
            quantity = production_line['product_qty'] - production_line['picking_qty']
            if quantity > 0:
                production_in_transit_line_ids.append((0, 0, {
                    'production_id': production_line['production_id'][0],
                    'quantity': quantity
                }))
                production_in_transit += quantity

        query = self.env['vision.availability.query'].create({
            'product_id': product_id,
            'quantity': quantity,
            'quantity_line_ids': quantity_line_ids,
            'purchase_in_transit': purchase_in_transit,
            'purchase_in_transit_line_ids': purchase_in_transit_line_ids,
            'sale_in_transit': sale_in_transit,
            'sale_in_transit_line_ids': sale_in_transit_line_ids,
            'production_in_transit': production_in_transit,
            'production_in_transit_line_ids': production_in_transit_line_ids,
            'availability': quantity + purchase_in_transit - sale_in_transit - production_in_transit
        })

        return {
            'name': _('库存可用量查询表'),
            'type': 'ir.actions.act_window',
            'res_model': 'vision.availability.query',
            'res_id': query.id,
            'view_mode': 'form',
            'target': 'new',
        }
