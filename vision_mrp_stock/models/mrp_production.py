# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductionReleaseInventory(models.TransientModel):
    _name = 'production.release.inventory'
    _description = '生产发布库存'

    name = fields.Char(string='名称', default='生产发布库存')
    # 生产单
    production_id = fields.Many2one('mrp.production', string='生产单')
    product_id = fields.Many2one('product.product', string='产品', related='production_id.product_id')
    # 订单数
    order_qty = fields.Integer(string='订单数', related='production_id.order_qty')
    # 已生产
    done_qty = fields.Integer(string='已生产', related='production_id.done_qty')
    # 生产数量
    product_qty = fields.Integer(string='本次生产', default=lambda self: self.order_qty - self.done_qty)

    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        for line in self.release_inventory_line:
            line.current_consumption_qty = self.product_qty * line.unit_factor

    # 生产发布库存明细
    release_inventory_line = fields.One2many('production.release.inventory.line', 'production_release_inventory_id',
                                             string='生产发布库存明细')

    # 生产发布库存
    def release_inventory(self):
        virtual_production_location_id = self.env.company.virtual_production_location_id
        finished_location_id = self.finished_location_id
        module_consume_location_id = self.module_consume_location_id
        product_qty = self.product_qty
        done_date = fields.Datetime.now()
        origin = self.production_id.name
        sale_origin = self.production_id.sale_order_id.name
        contract_no = self.production_id.contract_no
        # 生成成品库存移动
        main_product_move_id = self.env['stock.move'].create({
            'name': self.product_id.name,
            'product_id': self.product_id.id,
            'product_qty': product_qty,
            'product_uom_id': self.product_id.uom_id.id,
            'location_id': virtual_production_location_id.id,
            'location_dest_id': finished_location_id.id,
            'origin': origin,
            'sale_origin': sale_origin,
            'contract_no': contract_no,
            'state': 'done',
            'done_date': done_date,
            'production_id': self.production_id.id,
        })
        # 更新库存现有量
        self.env['stock.base.function'].update_stock_quantity(virtual_production_location_id, self.product_id,
                                                              -product_qty)
        self.env['stock.base.function'].update_stock_quantity(finished_location_id, self.product_id, product_qty)
        # 创建生产明细库存移动
        for line in self.release_inventory_line:
            if line.current_consumption_qty > 0:
                current_consumption_qty = line.current_consumption_qty
                self.env['stock.move'].create({
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_qty': current_consumption_qty,
                    'product_uom_id': line.product_id.uom_id.id,
                    'location_id': module_consume_location_id.id,
                    'location_dest_id': virtual_production_location_id.id,
                    'origin': origin,
                    'sale_origin': sale_origin,
                    'contract_no': contract_no,
                    'state': 'done',
                    'done_date': done_date,
                    'production_line_id': line.production_line_id.id,
                })
                # 更新库存现有量
                self.env['stock.base.function'].update_stock_quantity(module_consume_location_id, line.product_id,
                                                                      -line.current_consumption_qty)
                self.env['stock.base.function'].update_stock_quantity(virtual_production_location_id, line.product_id,
                                                                      line.current_consumption_qty)
                line.production_line_id.consume_qty += current_consumption_qty
        # 创建完工入库明细
        self.env['mrp.done.production.line'].create({
            'production_id': self.production_id.id,
            'product_id': self.product_id.id,
            'product_qty': product_qty,
            'done_date': done_date,
        })
        done_qty = self.done_qty + product_qty
        update_production_data = {'done_qty': done_qty, 'surplus_qty': done_qty - self.production_id.in_qty}
        # 如果已生产数 = 订单数，则修改状态
        if done_qty >= product_qty:
            update_production_data['state'] = 'done'
            update_production_data['end_date'] = done_date
        self.production_id.write(update_production_data)
        return {'type': 'ir.actions.act_window_close'}

    # 物料存放位置
    module_consume_location_id = fields.Many2one('stock.location', string='物料存放位置',
                                                 track_visibility='onchange')
    # 成品存放位置
    finished_location_id = fields.Many2one('stock.location', string='成品存放位置', track_visibility='onchange')

    # 虚拟生产车间
    virtual_production_location_id = fields.Many2one('stock.location', string='虚拟生产车间',
                                                     track_visibility='onchange')


class ProductionReleaseInventoryLine(models.TransientModel):
    _name = 'production.release.inventory.line'
    _description = '生产发布库存明细'

    production_release_inventory_id = fields.Many2one('production.release.inventory', string='生产发布库存')
    production_line_id = fields.Many2one('mrp.production.line', string='生产明细')
    product_id = fields.Many2one('product.product', string='产品', related='production_line_id.product_id')
    # 类别
    category_id = fields.Many2one('product.category', string='类别', related='product_id.category_id')
    # 条码
    barcode = fields.Char(string='条码', related='product_id.barcode')
    # 型号
    model = fields.Char(string='型号', related='product_id.model')
    # 图号
    drawing_number = fields.Char(string='图号', related='product_id.drawing_number')
    # 生产数
    product_qty = fields.Float(string='生产数', related='production_line_id.product_qty')
    # 领料数
    picking_qty = fields.Float(string='领料数', related='production_line_id.picking_qty')
    # 已消耗
    consume_qty = fields.Float(string='已消耗', related='production_line_id.consume_qty')
    # 本次消耗
    current_consumption_qty = fields.Float(string='本次消耗')
    # 单位
    product_uom_id = fields.Many2one('product.uom', string='单位', related='production_line_id.product_uom_id')
    # 单位因子
    unit_factor = fields.Float(string='用量', related='production_line_id.unit_factor')


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # 组件消耗位置
    module_consume_location_id = fields.Many2one('stock.location', string='组件消耗位置',
                                                 track_visibility='onchange',
                                                 default=lambda
                                                     self: self.env.company.finished_location_id.id)
    # 成品存放位置
    finished_location_id = fields.Many2one('stock.location',
                                           string='成品存放位置',
                                           track_visibility='onchange',
                                           default=lambda
                                               self: self.env.company.module_consume_location_id.id
                                           )
    # 虚拟生产车间
    virtual_production_location_id = fields.Many2one('stock.location', string='虚拟生产车间',
                                                     track_visibility='onchange',
                                                     default=lambda
                                                         self: self.env.company.virtual_production_location_id.id
                                                     )

    # 生产发布库存
    def open_release_inventory_action(self):
        if self.set_qty <= 0:
            raise UserError('齐套数小于1, 生产条件不满足！')
        product_qty = self.order_qty - self.done_qty
        release_inventory_id = self.env['production.release.inventory'].create({
            'production_id': self.id,
            'module_consume_location_id': self.module_consume_location_id.id,
            'finished_location_id': self.finished_location_id.id,
            'virtual_production_location_id': self.virtual_production_location_id.id,
            'product_qty': product_qty,
            'release_inventory_line': [(0, 0, {'production_line_id': line.id,
                                               'current_consumption_qty': product_qty * line.unit_factor
                                               }) for line in self.production_line]
        })
        # 弹窗打开生产发布库存动作
        return {
            'name': _('生产发布库存'),
            'type': 'ir.actions.act_window',
            'res_model': 'production.release.inventory',
            'view_mode': 'form',
            'res_id': release_inventory_id.id,
            'target': 'new',
        }
