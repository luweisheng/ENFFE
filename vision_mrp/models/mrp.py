# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    # 生产提前期
    production_lead_time = fields.Integer(string='生产提前期', default=30)
    # # 组件消耗位置
    # module_consume_location_id = fields.Many2one('stock.location', string='组件消耗位置', track_visibility='onchange')
    # # 成品存放位置
    # finished_location_id = fields.Many2one('stock.location', string='成品存放位置', track_visibility='onchange')
    # # 虚拟生产车间
    # virtual_production_location_id = fields.Many2one('stock.location', string='虚拟生产车间',
    #                                                  track_visibility='onchange')


class MrpProduction(models.Model):
    _name = 'mrp.production'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '生产单'

    name = fields.Char(string='单号', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    product_id = fields.Many2one('product.product', string='产品', required=True)

    product_uom_id = fields.Many2one('product.uom', string='单位', related='product_id.uom_id')
    # 类别
    category_id = fields.Many2one('product.category', string='产品类别', related='product_id.category_id')
    # 条码
    barcode = fields.Char(string='条码', related='product_id.barcode')
    # 型号
    model = fields.Char(string='型号', related='product_id.model')
    # 图号
    drawing_number = fields.Char(string='图号', related='product_id.drawing_number')
    origin = fields.Char(string='源单据')
    # BOM
    bom_id = fields.Many2one('mrp.bom', string='BOM', required=True, track_visibility='onchange',
                             related='product_id.bom_id')
    # 销售单
    sale_order_id = fields.Many2one('sale.order', string='销售单')
    # 合同号
    contract_no = fields.Char(string='合同号')
    # 订单数
    order_qty = fields.Integer(string='订单数')
    # 生产数
    product_qty = fields.Integer(string='生产数')
    # 已生产
    done_qty = fields.Integer(string='已生产')
    # 已入库
    in_qty = fields.Integer(string='已入库')
    # 剩余入库
    surplus_qty = fields.Integer(string='剩余入库')

    # @api.depends('done_qty', 'in_qty')
    # def _compute_surplus_qty(self):
    #     for production in self:
    #         production.surplus_qty = production.done_qty - production.in_qty
    #
    # @api.depends('done_line.product_qty')
    # def _compute_done_qty(self):
    #     for production in self:
    #         production.done_qty = sum(production.done_line.mapped('product_qty'))

    # 计划开始日期
    plan_start_date = fields.Date(string='计划开始日期')
    plan_end_date = fields.Date(string='计划结束日期')
    # 生产明细
    production_line = fields.One2many('mrp.production.line', 'production_id', string='生产明细')
    # 完工明细
    done_line = fields.One2many('mrp.done.production.line', 'production_id', string='完工明细')
    # 开始生产时间
    start_date = fields.Datetime(string='开始时间')
    end_date = fields.Datetime(string='结束时间')
    # 备注
    note = fields.Char(string='备注')
    state = fields.Selection([
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('underway', '正在生产'),
        ('done', '已完成'),
        ('cancel', '已取消'),
    ], string='状态', default='draft', track_visibility='onchange')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('mrp.production') or _("New")
        return super(MrpProduction, self).create(vals_list)

    # 开始生产
    def action_underway(self):
        self.write({'state': 'underway', 'start_date': fields.Datetime.now()})

    # 齐套数
    set_qty = fields.Float(string='齐套数', compute='_compute_set_qty')

    @api.depends('production_line.picking_qty')
    def _compute_set_qty(self):
        for production in self:
            production_line = [line.picking_qty - line.consume_qty for line in production.production_line]
            if production_line:
                production.set_qty = min(production_line)
            else:
                production.set_qty = 0

    is_outsource = fields.Boolean(string='委外', default=False)

    # 委外供应商
    supplier_id = fields.Many2one('res.supplier', string='供应商')

    # 生产工厂
    factory_id = fields.Many2one('production.factory', string='生产工厂')


class MrpProductionLine(models.Model):
    _name = 'mrp.production.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '生产明细'

    production_id = fields.Many2one('mrp.production', string='生产单')
    product_id = fields.Many2one('product.product', string='产品', required=True)
    # 类别
    category_id = fields.Many2one('product.category', string='类别', related='product_id.category_id')
    # 条码
    barcode = fields.Char(string='条码', related='product_id.barcode')
    # 型号
    model = fields.Char(string='型号', related='product_id.model')
    # 图号
    drawing_number = fields.Char(string='图号', related='product_id.drawing_number')
    bom_line_id = fields.Many2one('mrp.bom.line', string='BOM明细')
    # 生产数
    product_qty = fields.Float(string='生产数')
    # 领料数
    picking_qty = fields.Float(string='领料数')
    # 消耗数
    consume_qty = fields.Float(string='消耗数')
    # 单位
    product_uom_id = fields.Many2one('product.uom', string='单位', related='product_id.uom_id')
    # 单位因子
    unit_factor = fields.Float(string='用量')
    # bom备注
    bom_note = fields.Char(string='BOM备注')
    # 供应商
    supplier_id = fields.Many2one('res.supplier', string='供应商')
    # 价格表
    price_id = fields.Many2one('product.price', string='价格表')


class MrpDoneProductionLine(models.Model):
    _name = 'mrp.done.production.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '完工明细'

    production_id = fields.Many2one('mrp.production', string='生产单')
    product_id = fields.Many2one('product.product', string='产品')
    # 类别
    category_id = fields.Many2one('product.category', string='类别', related='product_id.category_id')
    # 条码
    barcode = fields.Char(string='条码', related='product_id.barcode')
    # 型号
    model = fields.Char(string='型号', related='product_id.model')
    # 图号
    drawing_number = fields.Char(string='图号', related='product_id.drawing_number')
    # 数量
    product_qty = fields.Integer(string='数量')
    # 单位
    product_uom_id = fields.Many2one('product.uom', string='单位', related='product_id.uom_id')
    # 完工时间
    done_date = fields.Datetime(string='完成时间')
