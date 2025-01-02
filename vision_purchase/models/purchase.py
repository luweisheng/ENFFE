# -*- coding: utf-8 -*-
from markupsafe import Markup

from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '采购单'

    _sql_constraints = [('name_uniq', 'unique(name)', '单号必须唯一')]

    name = fields.Char(string='单号', copy=False, readonly=True, index=True, default=lambda self: ('New'))
    origin = fields.Char(string='源单据')
    date_order = fields.Datetime(string='下单日期', copy=False, default=fields.Datetime.now, track_visibility='always')
    # 要求交期
    date_planned = fields.Datetime(string='要求交期', track_visibility='always')
    # 销售交期
    sale_date_planned = fields.Date(string='销售交期', related='sale_order_id.delivery_date')
    # 供应商
    supplier_id = fields.Many2one('res.supplier', string='供应商', required=True, track_visibility='always')

    @api.onchange('supplier_id')
    def _onchange_supplier_id(self):
        if self.supplier_id:
            self.tax_included = self.supplier_id.tax_included
            self.tax_rate = self.supplier_id.tax_rate

    # 采购员
    user_id = fields.Many2one('res.users', string='采购员', default=lambda self: self.env.user,
                              track_visibility='always')
    # 付款条款
    payment_term_id = fields.Many2one('res.payment.term', string='付款条款', track_visibility='always')
    # 贸易条款
    trade_term_id = fields.Many2one('res.trade.term', string='贸易条款', track_visibility='always')
    # 销售单
    sale_order_id = fields.Many2one('sale.order', string='销售单', track_visibility='always')
    # 合同号
    contract_no = fields.Char(string='合同号', track_visibility='always')
    # 采购行
    order_line = fields.One2many('purchase.order.line', 'order_id', string='采购行')
    # 采购清单
    order_line_list = fields.One2many('purchase.order.line.list', 'order_id', string='采购清单')

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
        ('confirm', '已报价'),
        ('done', '采购订单'),
        ('cancel', '取消'),
    ], string='状态', default='draft', track_visibility='always')

    def action_confirm(self):
        self.write({'state': 'confirm'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order') or _("New")
        return super(PurchaseOrder, self).create(vals_list)

    # 客户交期
    delivery_date = fields.Date(string='客户交期')

    @api.onchange('delivery_date')
    def _onchange_delivery_date(self):
        for line in self.order_line:
            line.delivery_date = self.delivery_date

    # 送货地址
    delivery_address_id = fields.Many2one('delivery.address', string='送货地址')

    @api.onchange('delivery_address_id')
    def _onchange_delivery_address(self):
        for line in self.order_line:
            line.delivery_address_id = self.delivery_address_id

    # 含税
    tax_included = fields.Boolean(string='含税')
    # 税率
    tax_rate = fields.Float(string='税率')


class PurchaseOrderLine(models.Model):
    _name = 'purchase.order.line'
    _description = '采购行'

    order_id = fields.Many2one('purchase.order', string='采购单')

    supplier_id = fields.Many2one('res.supplier', string='供应商', related='order_id.supplier_id', store=True)
    # 销售单号
    sale_order_id = fields.Many2one('sale.order', string='销售单', related='order_id.sale_order_id')
    # 价格表
    price_id = fields.Many2one('product.price', string='价格表')

    product_id = fields.Many2one('product.product', string='产品', required=True)
    # 类别
    category_id = fields.Many2one('product.category', string='类别', related='product_id.category_id', store=True)
    # 条码
    barcode = fields.Char(string='条码', related='product_id.barcode', store=True)
    # 型号
    model = fields.Char(string='型号', related='product_id.model', store=True)
    # 图号
    drawing_number = fields.Char(string='图号', related='product_id.drawing_number', store=True)
    product_qty = fields.Float(string='数量', default=1)
    origin_product_qty = fields.Float(string='订单数量', default=1)
    product_uom_id = fields.Many2one('product.uom', string='单位', related='product_id.po_uom_id', store=True)
    price_unit = fields.Float(string='单价', default=1)
    price_subtotal = fields.Float(string='小计', compute='_amount_line')
    # 下单产生的采购单
    is_auto = fields.Boolean(string='自动', default=False)

    @api.depends('product_qty', 'price_unit')
    def _amount_line(self):
        for line in self:
            line.price_subtotal = line.product_qty * line.price_unit

    # 客户交期
    delivery_date = fields.Date(string='客户交期')
    # 送货地址
    delivery_address_id = fields.Many2one('delivery.address', string='送货地址')
    # 下单日期
    date_order = fields.Datetime(string='下单日期', related='order_id.date_order')
    # 备注
    note = fields.Text(string='备注')

    @api.model_create_multi
    def create(self, vals_list):
        res = super(PurchaseOrderLine, self).create(vals_list)
        # 如果是手动添加的采购行，自动创建价格表
        for line in res:
            if not line.is_auto:
                price_id = self.env['product.price'].create({
                    'product_id': line.product_id.id,
                    'price': line.price_unit,
                    'name': line.order_id.supplier_id.id
                })
                line.write({'price_id': price_id.id})
                # 将添加产品记录到采购单备注栏
                body = """
                <ul class='text-success'>
                    <li>类型：采购明细添加</li>
                    <li>时间：{}</li>
                    <li>产品：{}</li>
                    <li>数量：{}</li>
                    <li>价格：{}</li>
                </ul>
                """.format(str(fields.Datetime.now()), line.product_id.name, line.product_qty, line.price_unit)
                res.order_id.message_post(body=Markup(body))
        return res

    def unlink(self):
        # 采购单备注栏记录删除产品
        for line in self:
            # 将添加产品记录到采购单备注栏
            body = """
                    <ul class='text-danger'>
                    <li>类型：采购明细删除</li>
                    <li>时间：{}</li>
                    <li>产品：{}</li>
                    <li>数量：{}</li>
                    <li>价格：{}</li>
                </ul>
                """.format(str(fields.Datetime.now()), line.product_id.name, line.product_qty, line.price_unit)
            line.order_id.message_post(body=Markup(body))
        return super(PurchaseOrderLine, self).unlink()

    order_line_list = fields.One2many('purchase.order.line.list', 'order_line_id', string='采购清单')


# 采购清单
class PurchaseOrderLineList(models.Model):
    _name = 'purchase.order.line.list'
    _inherit = 'purchase.order.line'
    _description = '采购清单'

    order_line_id = fields.Many2one('purchase.order.line', string='采购行')
    order_id = fields.Many2one('purchase.order', string='采购单', related='order_line_id.order_id')
    main_bom_id = fields.Many2one('mrp.bom', string='主BOM')
    bom_id = fields.Many2one('mrp.bom', string='归属BOM')
