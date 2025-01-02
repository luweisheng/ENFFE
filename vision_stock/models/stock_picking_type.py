# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockPickingType(models.Model):
    _name = 'stock.picking.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '单据类型'

    name = fields.Char(string='名称', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    sequence_id = fields.Many2one('ir.sequence', string='序列号')
    code = fields.Char(string='代码')
    # 源位置
    location_src_id = fields.Many2one('stock.location', string='源位置')

    # 原位置允许操作仓位
    location_src_permit_ids = fields.Many2many('stock.location',
                                               'stock_picking_type_location_src_permit_rel',
                                               string='源位置允许操作仓位')

    # 目标位置
    location_dest_id = fields.Many2one('stock.location', string='目标位置')
    # 目标位置允许操作仓位
    location_dest_permit_ids = fields.Many2many('stock.location',
                                                'stock_picking_type_location_dest_permit_rel',
                                                string='目标位置允许操作仓位')

    # 是否开启自动验证
    auto_validate = fields.Boolean(string='自动验证')