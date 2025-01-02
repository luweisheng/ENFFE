# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class OtherStock(models.TransientModel):
    _name = 'other.stock'
    _inherit = 'stock.allot.base'
    _description = '其他库存调拨'

    # 调拨方式，入库、出库
    allot_type = fields.Selection([('in', '入库'), ('out', '出库'), ('Internal', '内部调拨')], string='调拨方式', default='in')

    @api.onchange('allot_type')
    def _onchange_allot_type(self):
        allot_type = self.allot_type
        if allot_type == 'in':
            picking_type_id = self.env.company.other_in_stock_id
        elif allot_type == 'out':
            picking_type_id = self.env.company.other_out_stock_id
        else:
            picking_type_id = self.env.company.internal_transfer_id
        self.picking_type_id = picking_type_id.id
        self.location_id = picking_type_id.location_src_id.id
        self.location_dest_id = picking_type_id.location_dest_id.id

    # 其他入库明细
    other_stock_line_ids = fields.One2many('other.stock.line', 'other_stock_id', string='其他入库明细')

    @api.onchange('product_qty')
    def _other_onchange_product_qty(self):
        self.other_stock_line_ids.done_qty = self.product_qty

    @api.onchange('location_id', 'location_dest_id')
    def _other_onchange_location(self):
        for line in self.other_stock_line_ids:
            line.location_id = self.location_id
            line.location_dest_id = self.location_dest_id

    def create_stock_picking(self):
        self.ensure_one()
        # 创建调拨单
        picking_type_id = self.picking_type_id.id
        done_date = fields.Datetime.now()
        picking_data = {
            'name': self.picking_type_id.sequence_id.next_by_id(),
            'picking_type_id': picking_type_id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
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
                'location_id': line.location_id.id,
                'location_dest_id': line.location_dest_id.id,
                'contract_no': line.contract_no,
                'note': line.note,
                'state': 'done',
                'done_date': done_date,
                'done_qty': line_done_qty,
            }))
            self.env['stock.base.function'].update_stock_quantity(line.location_id, line.product_id, -line_done_qty)
            self.env['stock.base.function'].update_stock_quantity(line.location_dest_id, line.product_id, line_done_qty)
        stock_picking = self.env['stock.picking'].create(picking_data)
        # 跳转库存单据
        return {
            'name': _('调拨单据'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': stock_picking.id,
            'target': 'current',
        }


class OtherStockLine(models.TransientModel):
    _name = 'other.stock.line'
    _inherit = 'stock.allot.base.line'
    _description = '其他入库明细'

    other_stock_id = fields.Many2one('other.stock', string='其他入库')

    location_id = fields.Many2one('stock.location', string='源库位', default=lambda self: self.other_stock_id.location_id.id)
    location_dest_id = fields.Many2one('stock.location', string='目标库位', default=lambda self: self.other_stock_id.location_dest_id.id)

