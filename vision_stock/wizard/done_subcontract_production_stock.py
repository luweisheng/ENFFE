# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DoneSubcontractProductionStockLine(models.TransientModel):
    _name = 'done.subcontract.production.stock.line'
    _inherit = 'stock.allot.base.line'
    _description = '委外完工入库调拨明细'

    done_subcontract_production_stock_id = fields.Many2one('done.subcontract.production.stock', string='委外完工入库调拨')
    production_id = fields.Many2one('mrp.production', string='生产订单')
    # 已完工数量
    production_done_qty = fields.Integer(string='完工数', related='production_id.done_qty')


class DoneSubcontractProductionStock(models.TransientModel):
    _name = 'done.subcontract.production.stock'
    _inherit = 'stock.allot.base'
    _description = '委外完工入库调拨'

    production_ids = fields.Many2many('mrp.production', 'subcontract_done_production_stock_mrp_ids',
                                      string='委外订单',
                                      domain=[('state', 'in', ('confirmed', 'underway', 'done')), ('surplus_qty', '>', 0), ('is_outsource', '=', True)])
    # 入库明细
    done_subcontract_stock_line_ids = fields.One2many('done.subcontract.production.stock.line', 'done_subcontract_production_stock_id', string='委外完工入库明细')

    @api.onchange('product_qty')
    def _done_subcontract_production_onchange_product_qty(self):
        # 数量禁止小于0
        if self.product_qty < 0:
            raise UserError(_('数量不能小于0！'))
        self.done_subcontract_stock_line_ids.done_qty = self.product_qty

    @api.onchange('location_id', 'location_dest_id')
    def _done_subcontract_production_onchange_location(self):
        for line in self.done_subcontract_stock_line_ids:
            line.location_id = self.location_id
            line.location_dest_id = self.location_dest_id

    # 调拨方式，入库、退货
    allot_type = fields.Selection([('in', '入库'), ('return', '退货')], string='调拨方式', default='in')

    @api.onchange('allot_type')
    def _onchange_allot_type(self):
        picking_type_id = None
        allot_type = self.allot_type
        if allot_type == 'in':
            picking_type_id = self.env.company.finished_in_stock_id
        elif allot_type == 'return':
            picking_type_id = self.env.company.finished_return_id
        self.picking_type_id = picking_type_id.id
        self.location_id = picking_type_id.location_src_id.id
        self.location_dest_id = picking_type_id.location_dest_id.id

    @api.onchange('production_ids', 'picking_type_id', 'allot_type')
    def _production_set_stock_line_ids(self):
        production_ids = self.production_ids
        if production_ids:
            self.done_subcontract_stock_line_ids = None
            allot_type = self.allot_type
            location_id = self.location_id.id
            location_dest_id = self.location_dest_id.id
            stock_line_ids = []
            for production in production_ids:
                origin = production.name
                sale_origin = production.sale_order_id.name
                contract_no = production.sale_order_id.contract_no
                if allot_type == 'in':
                    done_qty = production.done_qty - production.in_qty
                else:
                    done_qty = production.in_qty
                stock_line_ids.append((0, 0, {
                    'product_id': production.product_id.id,
                    'uom_id': production.product_uom_id.id,
                    'done_qty': done_qty,
                    'location_id': location_id,
                    'location_dest_id': location_dest_id,
                    'origin': origin,
                    'sale_origin': sale_origin,
                    'contract_no': contract_no,
                    'production_id': production.id,
                }))
            self.done_subcontract_stock_line_ids = stock_line_ids

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
        for line in self.done_subcontract_stock_line_ids:
            line_done_qty = line.done_qty
            picking_data['move_line_ids'].append((0, 0, {
                'picking_type_id': picking_type_id,
                'product_id': line.product_id.id,
                'product_uom_id': line.uom_id.id,
                'product_qty': line_done_qty,
                'production_id': line.production_id.id,
                'location_id': line.location_id.id,
                'location_dest_id': line.location_dest_id.id,
                'origin': line.origin,
                'sale_origin': line.sale_origin,
                'contract_no': line.contract_no,
                'note': line.note,
                'state': 'done',
                'done_date': done_date,
                'done_qty': line_done_qty,
            }))
            # 物料消耗
            self.env['stock.base.function'].update_stock_quantity(line.location_id, line.product_id, -line_done_qty)
            self.env['stock.base.function'].update_stock_quantity(line.location_dest_id, line.product_id, line_done_qty)
            if allot_type == 'in':
                done_qty = line_done_qty
            else:
                done_qty = -line_done_qty
            # 更新生产订单已入库数
            line.production_id.in_qty += done_qty
            line.production_id.surplus_qty -= done_qty
        stock_picking = self.env['stock.picking'].create(picking_data)
        return {
            'name': _('库存单据'),
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'res_id': stock_picking.id,
        }


