# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


# 采购退货
class PurchaseStockReturn(models.TransientModel):
    _name = 'purchase.stock.return'
    _inherit = 'stock.allot.base'
    _description = '采购退货'

    sale_ids = fields.Many2many('sale.order', 'purchase_stock_sale_ids', string='销售订单')

    @api.onchange('sale_ids')
    def _sale_set_purchase_ids(self):
        purchase_ids = self.env['purchase.order'].search([('sale_order_id', 'in', self.sale_ids.ids)])
        self.purchase_ids = purchase_ids.ids

    purchase_ids = fields.Many2many('purchase.order', 'purchase_stock_purchase_ids', string='采购订单')

    @api.onchange('purchase_ids')
    def _purchase_set_stock_line_ids(self):
        if self.purchase_ids:
            self.stock_line_ids = None
            location_id = self.location_id.id
            location_dest_id = self.location_dest_id.id
            stock_line_ids = []
            for purchase in self.purchase_ids:
                origin = purchase.name
                sale_origin = purchase.sale_order_id.name
                contract_no = purchase.sale_order_id.contract_no
                supplier_id = purchase.supplier_id.id
                for line in purchase.order_line:
                    done_qty = line.product_qty - line.stock_qty
                    if done_qty > 0:
                        stock_line_ids.append((0, 0, {
                            'product_id': line.product_id.id,
                            'purchase_line_id': line.ids[0],
                            'uom_id': line.product_uom_id.id,
                            'done_qty': done_qty,
                            'location_id': location_id,
                            'location_dest_id': location_dest_id,
                            'origin': origin,
                            'sale_origin': sale_origin,
                            'contract_no': contract_no,
                            'supplier_id': supplier_id,
                        }))
            self.stock_line_ids = stock_line_ids

    # 供应商
    partner_ids = fields.Many2many('res.supplier', 'purchase_stock_partner_ids', string='供应商')

    @api.onchange('purchase_ids')
    def _purchase_return_set_stock_line_ids(self):
        if self.purchase_ids:
            self.stock_line_ids = None
            location_id = self.location_id.id
            location_dest_id = self.location_dest_id.id
            stock_line_ids = []
            for purchase in self.purchase_ids:
                origin = purchase.name
                sale_origin = purchase.sale_order_id.name
                contract_no = purchase.sale_order_id.contract_no
                supplier_id = purchase.supplier_id.id
                for line in purchase.order_line:
                    done_qty = line.stock_qty
                    if done_qty > 0:
                        stock_line_ids.append((0, 0, {
                            'product_id': line.product_id.id,
                            'purchase_line_id': line.ids[0],
                            'uom_id': line.product_uom_id.id,
                            'done_qty': done_qty,
                            'location_id': location_id,
                            'location_dest_id': location_dest_id,
                            'origin': origin,
                            'sale_origin': sale_origin,
                            'contract_no': contract_no,
                            'supplier_id': supplier_id,
                        }))
            self.purchase_stock_return_line_ids = stock_line_ids

    @api.model
    def default_get(self, fields):
        res = super(PurchaseStockReturn, self).default_get(fields)
        picking_type = self.env.context.get('picking_type')
        if picking_type == 'CGTH':
            purchase_in_stock_id = self.env.company.purchase_in_stock_id
            res['picking_type_id'] = purchase_in_stock_id.id
            res['location_id'] = purchase_in_stock_id.location_src_id.id
            res['location_dest_id'] = purchase_in_stock_id.location_dest_id.id
        return res

    @api.onchange('partner_ids')
    def _partner_set_purchase_ids(self):
        purchase_ids = self.env['purchase.order'].search([('supplier_id', 'in', self.partner_ids.ids)])
        self.purchase_ids = purchase_ids.ids

    # 入库明细
    purchase_stock_return_line_ids = fields.One2many('purchase.stock.return.line', 'purchase_return_stock_id', string='退货明细')

    def create_stock_picking(self):
        sale_origin = []
        contract_no = []
        origin = []
        supplier_name = []
        for purchase_id in self.purchase_ids:
            sale_name = purchase_id.sale_order_id.name
            sale_contract_no = purchase_id.sale_order_id.contract_no
            purchase_supplier_name = purchase_id.supplier_id.name
            if sale_name and sale_name not in sale_origin:
                sale_origin.append(sale_name)
            if sale_contract_no and sale_contract_no not in contract_no:
                contract_no.append(sale_contract_no)
            if purchase_supplier_name and purchase_supplier_name not in supplier_name:
                supplier_name.append(purchase_supplier_name)
            origin.append(purchase_id.name)
        sale_origin = ','.join(sale_origin)
        contract_no = ','.join(contract_no)
        origin = ','.join(origin)
        supplier_name = ','.join(supplier_name)
        picking_type_id = self.picking_type_id.id
        done_date = fields.Datetime.now()
        picking_data = {
            'name': self.picking_type_id.sequence_id.next_by_id(),
            'picking_type_id': picking_type_id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'origin': origin,
            'sale_origin': sale_origin,
            'contract_no': contract_no,
            'state': 'done',
            'note': self.note,
            'done_date': done_date,
            'supplier_name': supplier_name,
            'move_line_ids': []
        }
        for line in self.stock_line_ids:
            picking_data['move_line_ids'].append((0, 0, {
                'picking_type_id': picking_type_id,
                'product_id': line.product_id.id,
                'product_uom_id': line.purchase_uom_id.id,
                'product_qty': line.done_qty,
                'location_id': line.location_id.id,
                'location_dest_id': line.location_dest_id.id,
                'origin': line.origin,
                'sale_origin': line.sale_origin,
                'contract_no': line.contract_no,
                'purchase_line_id': line.purchase_line_id.id,
                'note': line.note,
                'purchase_price': line.purchase_price,
                'supplier_id': line.supplier_id.id,
                'state': 'done',
                'done_date': done_date,
                'done_qty': line.done_qty,
            }))
            # 更新采购明细入库数
            line.purchase_line_id.stock_qty += line.done_qty
            self.env['stock.base.function'].update_stock_quantity(line.location_id, line.product_id, -line.done_qty)
            self.env['stock.base.function'].update_stock_quantity(line.location_dest_id, line.product_id, line.done_qty)

        stock_picking = self.env['stock.picking'].create(picking_data)
        # 更新采购单入库情况

        # 跳转库存单据
        return {
            'name': _('采购退货'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': stock_picking.id,
            'target': 'current',
        }


class PurchaseStockReturnLine(models.TransientModel):
    _name = 'purchase.stock.return.line'
    _inherit = 'stock.allot.base.line'
    _description = '采购退货明细'

    purchase_return_stock_id = fields.Many2one('purchase.stock.return', string='采购退货')
    # 采购明细
    purchase_line_id = fields.Many2one('purchase.order.line', string='采购明细')
    # 采购数量
    purchase_qty = fields.Float(string='采购数量', related='purchase_line_id.product_qty')
    purchase_price = fields.Float(string='采购价格', related='purchase_line_id.price_unit')
    # 采购单位
    uom_id = fields.Many2one('product.uom', string='单位')
    # 已入库数量
    stock_qty = fields.Float(string='已入库', related='purchase_line_id.stock_qty')
    supplier_id = fields.Many2one('res.supplier', string='供应商')