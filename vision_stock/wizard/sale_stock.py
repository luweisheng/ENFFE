# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleStockOut(models.TransientModel):
    _name = 'sale.stock.out'
    _inherit = 'stock.allot.base'
    _description = '销售出库'

    sale_order_ids = fields.Many2many('sale.order', 'sale_stock_out_sale_ids', string='销售订单', domain=[('state', '=', 'done')])
    # 出库明细
    sale_stock_out_line_ids = fields.One2many('sale.stock.out.line', 'sale_stock_out_id', string='销售出库明细')

    @api.onchange('product_qty')
    def _sale_onchange_product_qty(self):
        # 数量禁止小于0
        if self.product_qty < 0:
            raise UserError(_('数量不能小于0！'))
        self.sale_stock_out_line_ids.done_qty = self.product_qty

    @api.onchange('location_id', 'location_dest_id')
    def _sale_onchange_location(self):
        for line in self.sale_stock_out_line_ids:
            line.location_id = self.location_id
            line.location_dest_id = self.location_dest_id

    @api.onchange('sale_order_ids', 'picking_type_id', 'allot_type')
    def _sale_order_set_stock_line_ids(self):
        sale_order_ids = self.sale_order_ids
        if sale_order_ids:
            self.sale_stock_out_line_ids = None
            location_id = self.location_id.id
            location_dest_id = self.location_dest_id.id
            stock_line_ids = []
            allot_type = self.allot_type
            for sale_order in sale_order_ids:
                for line in sale_order.order_line:
                    if allot_type == 'out':
                        done_qty = line.product_uom_qty - line.qty_delivered
                    else:
                        done_qty = line.qty_delivered
                    if done_qty > 0:
                        stock_line_ids.append((0, 0, {
                            'product_id': line.product_id.id,
                            'sale_line_id': line.ids[0],
                            'uom_id': line.product_uom_id.id,
                            'done_qty': done_qty,
                            'location_id': location_id,
                            'location_dest_id': location_dest_id,
                        }))
            self.sale_stock_out_line_ids = stock_line_ids

    def create_stock_picking(self):
        sale_origin = []
        contract_no = []
        origin = []
        allot_type = self.allot_type
        for sale in self.sale_order_ids:
            sale_name = sale.name
            sale_contract_no = sale.contract_no
            if sale_name and sale_name not in sale_origin:
                sale_origin.append(sale_name)
            if sale_contract_no and sale_contract_no not in contract_no:
                contract_no.append(sale_contract_no)
            origin.append(sale.name)
        sale_origin = ','.join(sale_origin)
        contract_no = ','.join(contract_no)
        origin = ','.join(origin)
        picking_type_id = self.picking_type_id.id
        done_date = fields.Datetime.now()
        location_id = self.location_id.id
        location_dest_id = self.location_dest_id.id
        picking_data = {
            'name': self.picking_type_id.sequence_id.next_by_id(),
            'picking_type_id': picking_type_id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'origin': origin,
            'sale_origin': sale_origin,
            'contract_no': contract_no,
            'state': 'done',
            'note': self.note,
            'done_date': done_date,
            'move_line_ids': []
        }
        for line in self.sale_stock_out_line_ids:
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
                'sale_line_id': line.sale_line_id.id,
                'note': line.note,
                'state': 'done',
                'done_date': done_date,
                'done_qty': line_done_qty,
            }))
            if allot_type == 'out':
                done_qty = line_done_qty
            else:
                done_qty = -line_done_qty
            # 更新销售出货明细
            line.sale_line_id.qty_delivered += done_qty
            if line.sale_line_id.bom_id.bom_type != 'phantom':
                self.env['stock.base.function'].update_stock_quantity(line.location_id, line.product_id, -line_done_qty)
                self.env['stock.base.function'].update_stock_quantity(line.location_dest_id, line.product_id, line_done_qty)
            else:
                for bom_line in line.sale_line_id.bom_id.bom_line_ids:
                    self.env['stock.base.function'].update_stock_quantity(line.location_id, bom_line.product_id, -line_done_qty * bom_line.product_qty)
                    self.env['stock.base.function'].update_stock_quantity(line.location_dest_id, bom_line.product_id, line_done_qty * bom_line.product_qty)

        stock_picking = self.env['stock.picking'].create(picking_data)
        return {
            'name': _('销售库存移动'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'res_id': stock_picking.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
    # 调拨方式：出货、退货
    allot_type = fields.Selection([('out', '出货'), ('return', '退货')], string='调拨方式', default='out')

    @api.onchange('allot_type')
    def _onchange_allot_type(self):
        picking_type_id = None
        allot_type = self.allot_type
        if allot_type == 'out':
            picking_type_id = self.env.company.sale_out_stock_id
        elif allot_type == 'return':
            picking_type_id = self.env.company.sale_return_id
        self.picking_type_id = picking_type_id.id
        self.location_id = picking_type_id.location_src_id.id
        self.location_dest_id = picking_type_id.location_dest_id.id


class SaleStockOutLine(models.TransientModel):
    _name = 'sale.stock.out.line'
    _inherit = 'stock.allot.base.line'
    _description = '销售出库明细'

    sale_stock_out_id = fields.Many2one('sale.stock.out', string='销售出库')
    sale_line_id = fields.Many2one('sale.order.line', string='销售订单行')