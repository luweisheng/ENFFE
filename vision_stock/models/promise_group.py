# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    # 采购入库单
    purchase_in_stock_id = fields.Many2one('stock.picking.type', string="采购入库单")
    # 采购退货单
    purchase_return_id = fields.Many2one('stock.picking.type', string="采购退货单")
    # 销售出库单
    sale_out_stock_id = fields.Many2one('stock.picking.type', string="销售出库单")
    # 销售退货单
    sale_return_id = fields.Many2one('stock.picking.type', string="销售退货单")
    # 生产领料
    production_out_stock_id = fields.Many2one('stock.picking.type', string="生产领料单")
    # 生产退料
    production_return_id = fields.Many2one('stock.picking.type', string="生产退料单")
    # 完工入库
    finished_in_stock_id = fields.Many2one('stock.picking.type', string="完工入库单")
    # 完工退库
    finished_return_id = fields.Many2one('stock.picking.type', string="完工退库单")
    # 委外发料
    outsource_out_stock_id = fields.Many2one('stock.picking.type', string="委外发料单")
    # 委外退料
    outsource_return_id = fields.Many2one('stock.picking.type', string="委外退料单")
    # 委外入库
    outsource_in_stock_id = fields.Many2one('stock.picking.type', string="委外入库单")
    # 委外退库
    outsource_return_stock_id = fields.Many2one('stock.picking.type', string="委外退库单")
    # 其他入库
    other_in_stock_id = fields.Many2one('stock.picking.type', string="其它入库单")
    # 其他出库
    other_out_stock_id = fields.Many2one('stock.picking.type', string="其它出库单")
    # 内部调拨
    internal_transfer_id = fields.Many2one('stock.picking.type', string="内部调拨单")