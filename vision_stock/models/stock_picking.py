# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '库存移动'

    name = fields.Char(string='名称', copy=False, index=True, default=lambda self: _('New'))
    # 单据类型
    picking_type_id = fields.Many2one('stock.picking.type', string='单据类型', required=True)
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
    supplier_name = fields.Char(string='供应商')
    # 客户
    corporation_id = fields.Many2one('res.corporation', string='客户')
    corporation_name = fields.Char(string='客户')
    # 销售单
    sale_order_id = fields.Many2one('sale.order', string='销售单')
    # 采购订单
    purchase_id = fields.Many2one('purchase.order', string='采购订单')
    # 制造单
    production_id = fields.Many2one('mrp.production', string='制造单')
    # 合同号
    contract_no = fields.Char(string='合同号')
    origin = fields.Char(string='源单据')
    # 单据日期
    done_date = fields.Datetime(string='单据日期', readonly=True)
    sale_origin = fields.Char(string='销售源')
    # 序列号
    sequence_id = fields.Many2one('ir.sequence', string='序列号')
    # 移动行
    move_line_ids = fields.One2many('stock.move', 'picking_id', string='移动行')
    note = fields.Text(string='备注')

    # 取消
    def action_cancel(self):
        self.write({'state': 'cancel'})

    # def refresh_stock_move(self, stock_move):
    #     done_qty = stock_move.done_qty
    #     stock_move.write({'state': 'done'})
    #     self.env['stock.base.function'].update_stock_quantity(stock_move.location_id, stock_move.product_id, -done_qty)
    #     self.env['stock.base.function'].update_stock_quantity(stock_move.location_dest_id, stock_move.product_id, done_qty)
    #     if stock_move.purchase_order_line:
    #         if stock_move.stock_change_type == 'add':
    #             stock_move.purchase_order_line.write({'done_qty': stock_move.purchase_order_line.done_qty + done_qty})
    #         else:
    #             stock_move.purchase_order_line.write({'done_qty': stock_move.purchase_order_line.done_qty - done_qty})
    #         # 更新采购
    #     elif stock_move.sale_order_line:
    #         if stock_move.stock_change_type == 'add':
    #             stock_move.sale_order_line.write({'done_qty': stock_move.sale_order_line.done_qty + done_qty})
    #         else:
    #             stock_move.sale_order_line.write({'done_qty': stock_move.sale_order_line.done_qty - done_qty})
    #     elif stock_move.production_order_line:
    #         if stock_move.stock_change_type == 'add':
    #             stock_move.production_order_line.write({'done_qty': stock_move.production_order_line.done_qty + done_qty})
    #         else:
    #             stock_move.production_order_line.write({'done_qty': stock_move.production_order_line.done_qty - done_qty})
    #
    # def action_confirm(self):
    #     self.write({'state': 'done'})
    #     for line in self.move_line_ids:
    #         line.refresh_stock_move(line)



