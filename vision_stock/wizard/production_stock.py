# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductionStock(models.TransientModel):
    _name = 'production.stock'
    _inherit = 'stock.allot.base'
    _description = '生产调拨'

    sale_ids = fields.Many2many('sale.order', 'production_stock_sale_ids', string='销售订单')
    production_ids = fields.Many2many('mrp.production', 'production_stock_mrp_ids', string='生产订单')
    # 入库明细
    stock_line_ids = fields.One2many('production.stock.line', 'production_stock_id', string='生产领料明细')

    @api.onchange('product_qty')
    def _production_onchange_product_qty(self):
        # 数量禁止小于0
        if self.product_qty < 0:
            raise UserError(_('数量不能小于0！'))
        self.stock_line_ids.done_qty = self.product_qty

    @api.onchange('location_id', 'location_dest_id')
    def _production_onchange_location(self):
        for line in self.stock_line_ids:
            line.location_id = self.location_id
            line.location_dest_id = self.location_dest_id

    allot_type = fields.Selection([('in', '领料'), ('return', '退料')], string='调拨方式', default='in')

    @api.onchange('allot_type')
    def _onchange_allot_type(self):
        picking_type_id = None
        allot_type = self.allot_type
        if allot_type == 'in':
            picking_type_id = self.env.company.production_out_stock_id
        elif allot_type == 'return':
            picking_type_id = self.env.company.production_return_id
        self.picking_type_id = picking_type_id.id
        self.location_id = picking_type_id.location_src_id.id
        self.location_dest_id = picking_type_id.location_dest_id.id

    def create_stock_picking(self):
        sale_origin = []
        contract_no = []
        origin = []
        allot_type = self.allot_type
        for production in self.production_ids:
            sale_name = production.sale_order_id.name
            sale_contract_no = production.sale_order_id.contract_no
            if sale_name and sale_name not in sale_origin:
                sale_origin.append(sale_name)
            if sale_contract_no and sale_contract_no not in contract_no:
                contract_no.append(sale_contract_no)
            origin.append(production.name)
        sale_origin = ','.join(sale_origin)
        contract_no = ','.join(contract_no)
        origin = ','.join(origin)
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
            'move_line_ids': []
        }
        for line in self.stock_line_ids:
            line_done_qty = line.done_qty
            picking_data['move_line_ids'].append((0, 0, {
                'picking_type_id': picking_type_id,
                'product_id': line.product_id.id,
                'product_uom_id': line.uom_id.id,
                'product_qty': line_done_qty,
                'location_id': line.location_id.id,
                'location_dest_id': line.location_dest_id.id,
                'origin': line.origin,
                'sale_origin': line.sale_origin,
                'contract_no': line.contract_no,
                'production_line_id': line.production_line_id.id,
                'note': line.note,
                'supplier_id': line.supplier_id.id,
                'state': 'done',
                'done_date': done_date,
                'done_qty': line_done_qty,
            }))
            if allot_type == 'in':
                done_qty = line_done_qty
            else:
                done_qty = -line_done_qty
            # 更新采购明细入库数
            line.production_line_id.picking_qty += done_qty
            self.env['stock.base.function'].update_stock_quantity(line.location_id, line.product_id, -line_done_qty)
            self.env['stock.base.function'].update_stock_quantity(line.location_dest_id, line.product_id, line_done_qty)

        stock_picking = self.env['stock.picking'].create(picking_data)
        # 更新采购单入库情况
        # 跳转库存单据
        return {
            'name': _('生产领料'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': stock_picking.id,
            'target': 'current',
        }

    @api.onchange('production_ids', 'picking_type_id', 'allot_type')
    def _production_set_stock_line_ids(self):
        production_ids = self.production_ids
        if production_ids:
            self.stock_line_ids = None
            location_id = self.location_id.id
            location_dest_id = self.location_dest_id.id
            stock_line_ids = []
            allot_type = self.allot_type
            for production in production_ids:
                origin = production.name
                sale_origin = production.sale_order_id.name
                contract_no = production.sale_order_id.contract_no
                for line in production.production_line:
                    if allot_type == 'in':
                        done_qty = line.product_qty - line.picking_qty
                    else:
                        done_qty = line.picking_qty
                    supplier_id = line.supplier_id.id
                    if done_qty > 0:
                        stock_line_ids.append((0, 0, {
                            'product_id': line.product_id.id,
                            'production_line_id': line.ids[0],
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


class ProductionStockLine(models.TransientModel):
    _name = 'production.stock.line'
    _inherit = 'stock.allot.base.line'
    _description = '生产调拨明细'

    production_stock_id = fields.Many2one('production.stock', string='生产调拨')
    # 生产明细
    production_line_id = fields.Many2one('mrp.production.line', string='生产明细')
    # 生产数
    production_qty = fields.Float(related='production_line_id.product_qty')
    # 领料数
    production_done_qty = fields.Float(related='production_line_id.picking_qty')

    supplier_id = fields.Many2one('res.supplier', string='供应商')





