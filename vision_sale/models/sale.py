# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '销售单'

    _sql_constraints = [('name_uniq', 'unique(name)', '单号必须唯一')]

    name = fields.Char(string='单号', copy=False, readonly=True, index=True, default=lambda self: ('New'))
    date_order = fields.Datetime(string='下单日期', copy=False, default=fields.Datetime.now, track_visibility='always')
    # 客户
    corporation_id = fields.Many2one('res.corporation', string='客户', required=True, track_visibility='always')
    # 合同号
    contract_no = fields.Char(string='合同号', track_visibility='always')
    # 交期
    delivery_date = fields.Date(string='交货日期', track_visibility='always')
    # 销售员
    user_id = fields.Many2one('res.users', string='销售员', default=lambda self: self.env.user, track_visibility='always')
    # 销售团队
    team_id = fields.Many2one('res.team', string='销售团队')
    # 交货地址
    delivery_address_id = fields.Many2one('delivery.address', string='交货地址')
    # 订单类型
    sale_type_id = fields.Many2one('sale.type', string='订单类型')
    # 付款条款
    payment_term_id = fields.Many2one('payment.terms', string='付款条款')
    # 包装类型
    packing_type_id = fields.Many2one('packing.type', string='包装类型')
    # 交货工厂
    factory_id = fields.Many2one('production.factory', string='生产工厂')

    @api.onchange('factory_id')
    def _onchange_factory_id(self):
        if self.factory_id:
            self.order_line = self.factory_id.id

    # 船运日期
    ship_date = fields.Date(string='船运日期')

    origin = fields.Char(string='源单据')

    # 是否含税
    tax_included = fields.Boolean(string='含税', default=False)

    # 下单方式，订单需求、库存需求、卖库存
    order_type = fields.Selection([
        ('order', '订单需求'),
        ('sell', '卖库存')
    ], string='下单方式', default='order', required=True)

    # 订单行
    order_line = fields.One2many('sale.order.line', 'order_id', string='订单行', copy=True)

    # 计算金额
    @api.depends('order_line.price_subtotal')
    def _amount_all(self):
        for order in self:
            amount_total = 0.0
            for line in order.order_line:
                amount_total += line.price_subtotal
            order.update({
                'amount_total': amount_total,
            })

    # 总金额
    amount_total = fields.Float(string='总金额', compute='_amount_all')

    # 状态
    state = fields.Selection([
        ('draft', '草稿'),
        ('offer', '报价'),
        ('done', '销售订单'),
        ('cancel', '取消'),
    ], string='状态', default='draft', track_visibility='always')

    # 报价
    def action_offer(self):
        self.write({'state': 'offer'})

    # 下单
    def action_done(self):
        self.write({'state': 'done'})

    # 取消
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or _("New")
        return super(SaleOrder, self).create(vals_list)

    # 税率
    tax_rate = fields.Float(string='税率')


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _description = '销售单行'

    order_id = fields.Many2one('sale.order', string='销售单', required=True, ondelete='cascade', index=True, copy=False)
    # 产品
    product_id = fields.Many2one('product.product', string='产品', domain=[('sale_ok', '=', True)], required=True)
    # 类别
    category_id = fields.Many2one('product.category', string='类别', related='product_id.category_id', store=True)
    # 类别序号
    sequence = fields.Integer(related='category_id.sequence', string='序号')
    # 条码
    barcode = fields.Char(string='条码', related='product_id.barcode', store=True)
    # 型号
    model = fields.Char(string='型号', related='product_id.model', store=True)
    # 数量
    product_uom_qty = fields.Float(string='数量', digits='Product Unit of Measure', required=True, default=1)
    # 单位
    product_uom_id = fields.Many2one('product.uom', string='单位', related='product_id.uom_id')
    # 价格表
    price_id = fields.Many2one('product.price', string='价格表', domain="[('product_id', '=', product_id)]")

    @api.onchange('price_id')
    def _onchange_price_id(self):
        if self.price_id:
            self.price_suggest = self.price_id.price

    # bom
    bom_id = fields.Many2one('mrp.bom', string='BOM', related='product_id.bom_id')

    @api.onchange('bom_id')
    def _onchange_bom_id(self):
        self.price_suggest = self.bom_id.total_cost

    # 单价
    price_unit = fields.Float(string='单价', required=True, digits='Product Price', default=1)

    @api.depends('price_unit', 'order_id.tax_rate')
    def _compute_price_tax(self):
        for line in self:
            line.price_tax = line.price_unit

    # 含税单价
    price_tax = fields.Float(string='含税单价', compute='_compute_price_tax')

    # 计算小计
    @api.depends('product_uom_qty', 'price_tax')
    def _compute_price_tax_subtotal(self):
        for line in self:
            line.price_tax_subtotal = line.product_uom_qty * line.price_tax

    # 含税小计
    price_tax_subtotal = fields.Float(string='含税小计', compute='_compute_price_tax_subtotal')

    # 计算小计
    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount(self):
        for line in self:
            line.price_subtotal = line.product_uom_qty * line.price_unit

    # 金额
    price_subtotal = fields.Float(string='小计', compute='_compute_amount')
    # 建议售价
    price_suggest = fields.Float(string='建议售价')
    # 备注
    remark = fields.Text(string='备注')

    qty_delivered = fields.Float(string='已交货数量', readonly=True, default=0)
    factory_id = fields.Many2one('production.factory', string='生产工厂')

