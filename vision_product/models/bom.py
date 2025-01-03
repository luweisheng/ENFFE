# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from markupsafe import Markup


# 设计标准
class DesignStandard(models.Model):
    _name = 'design.standard'
    _description = '设计标准'

    name = fields.Char(string='名称', required=True)
    code = fields.Char(string='编码')
    note = fields.Text(string='备注')


class MrpBomTemplate(models.Model):
    _name = 'mrp.bom.template'
    _description = 'BOM模板'

    name = fields.Char(string='名称', required=True)
    # 适用类别
    category_ids = fields.Many2many('product.category', 'MrpBomTemplatecategory_id', string='适用类别')
    # bom行
    bom_line = fields.One2many('mrp.bom.template.line', 'bom_template_id', string='BOM明细')


class MrpBomTemplateLine(models.Model):
    _name = 'mrp.bom.template.line'
    _description = 'BOM模板明细'

    bom_template_id = fields.Many2one('mrp.bom.template', string='BOM模板')
    # 类别
    category_id = fields.Many2one('product.category', string='类别')
    sequence = fields.Integer(related='category_id.sequence', string='NO', store=True)


class MrpBom(models.Model):
    _name = 'mrp.bom'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'BOM'

    _sql_constraints = [('name_uniq', 'unique(name)', '编号必须唯一'),
                        ('product_id_uniq', 'unique(product_id)', '每款产品只能拥有1个BOM!')]

    name = fields.Char(string='编号', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    product_id = fields.Many2one('product.product', string='产品', required=True, track_visibility='always', copy=False)
    # 类别
    category_id = fields.Many2one('product.category', string='类别', related='product_id.category_id')
    # 条码
    barcode = fields.Char(string='条码', related='product_id.barcode')
    # 型号
    model = fields.Char(string='型号', related='product_id.model')
    # 图号
    drawing_number = fields.Char(string='图号', related='product_id.drawing_number')

    bom_type = fields.Selection([
        ('production', '制造'),
        ('phantom', '套件'),
        ('subcontractor', '委外')
    ], string='类型', default='production', required=True)

    bom_line = fields.One2many('mrp.bom.line', 'bom_id', string='BOM明细')

    @api.depends('bom_line.price')
    def _compute_purchase_cost(self):
        for bom in self:
            bom.purchase_cost = sum(line.price for line in bom.bom_line)

    # 采购成本
    purchase_cost = fields.Float(string='采购总价', compute='_compute_purchase_cost', track_visibility='always')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'mrp.bom') or _("New")
        res = super(MrpBom, self).create(vals_list)
        res.product_id.bom_id = res.id
        return res

    def _ergodic_bom_line(self, line, data):
        for bom_line in line:
            if bom_line.product_id.bom_id:
                self._ergodic_bom_line(bom_line.bom_id.bom_line, data)
            else:
                if bom_line.price_id:
                    data.append((0, 0, {
                        'bom_line_id': bom_line.id,
                        'supplier_id': bom_line.price_id.name.id,
                        'price': bom_line.price_id.price,
                        'min_qty': bom_line.price_id.min_qty,
                        'note': bom_line.price_id.note
                    }))
                else:
                    data.append((0, 0, {
                        'bom_line_id': bom_line.id,
                        'supplier_id': False,
                        'price': 1,
                        'min_qty': 1,
                        'note': ''
                    }))
        return data

    def bulk_maintenance_price_list(self):
        line_ids = []
        self._ergodic_bom_line(self.bom_line, line_ids)
        res_id = self.env['bulk.maintenance.price'].create({
            'name': '批量维护价格表',
            'line_ids': line_ids
        })
        return {
            'name': '批量维护价格表',
            'view_mode': 'form',
            'res_model': 'bulk.maintenance.price',
            'type': 'ir.actions.act_window',
            'res_id': res_id.id,
            'target': 'new',
        }

    state = fields.Selection([('draft', '初稿制作'),
                              ('purchase', '采购核价'),
                              ('sale', '业务确认'),
                              ('technical_review', '技术复核'),
                              ('done', '配置完成')],
                             string='状态',
                             default='draft',
                             required=True,
                             track_visibility='always')

    # bom提交下一步
    def action_next(self):
        state = {
            'draft': 'purchase',
            'purchase': 'sale',
            'sale': 'technical_review',
            'technical_review': 'done',
        }
        self.write({'state': state[self.state]})

    # 提交采购审核人员
    submit_purchase_user_id = fields.Many2one('res.users', string='提交采购审核人员')
    # 提交采购审核时间
    submit_purchase_time = fields.Datetime(string='提交采购审核时间')

    def action_submit_purchase(self):
        self.write({'state': 'purchase',
                    'submit_purchase_user_id': self.env.uid,
                    'submit_purchase_time': fields.Datetime.now()})

    def action_reject_purchase(self):
        self.write({'state': 'draft'})

    # 提交业务审核人员
    submit_sale_user_id = fields.Many2one('res.users', string='提交业务审核人员')
    # 提交业务审核时间
    submit_sale_time = fields.Datetime(string='提交业务审核时间')

    def action_submit_sale(self):
        self.write({'state': 'sale',
                    'submit_sale_user_id': self.env.uid,
                    'submit_sale_time': fields.Datetime.now()})

    def action_reject_sale(self):
        self.write({'state': 'purchase'})

    # 提交技术审核人员
    submit_technical_review_user_id = fields.Many2one('res.users', string='提交技术审核人员')
    # 提交技术审核时间
    submit_technical_review_time = fields.Datetime(string='提交技术审核时间')

    def action_submit_technical_review(self):
        self.write({'state': 'technical_review',
                    'submit_technical_review_user_id': self.env.uid,
                    'submit_technical_review_time': fields.Datetime.now()})

    def action_reject_technical_review(self):
        self.write({'state': 'sale'})

    # 提交配置完成
    submit_done_user_id = fields.Many2one('res.users', string='完成时间')
    # 提交配置完成时间
    submit_done_time = fields.Datetime(string='审核完成时间')

    def action_submit_done(self):
        self.write({'state': 'done',
                    'submit_done_user_id': self.env.uid,
                    'submit_done_time': fields.Datetime.now()})

    def action_reject_done(self):
        self.write({'state': 'technical_review'})

    # bom提交上一步
    def action_previous(self):
        state = {
            'purchase': 'draft',
            'sale': 'purchase',
            'technical_review': 'sale',
            'done': 'technical_review',
        }
        self.write({'state': state[self.state]})

    # 委外加工商
    subcontractor_id = fields.Many2one('res.supplier', string='委外加工商', track_visibility='always')
    # 设计标准
    design_standard_id = fields.Many2one('design.standard', string='设计标准', track_visibility='always')
    # 包装方式
    packing_type_id = fields.Many2one('packing.type', string='包装方式', track_visibility='always')
    # 长
    length = fields.Float(string='长', related='packing_type_id.length')
    # 宽
    width = fields.Float(string='宽', related='packing_type_id.width')
    # 高
    height = fields.Float(string='高', related='packing_type_id.height')
    gp20 = fields.Integer(string='20GP', track_visibility='always')
    gp40 = fields.Integer(string='40GP', track_visibility='always')
    gp40hq = fields.Integer(string='40HQ', track_visibility='always')

    # 工厂加工费
    factory_cost = fields.Float(string='工厂加工费', track_visibility='always')

    # 总费用
    total_cost = fields.Float(string='总费用', compute='_compute_total_cost', track_visibility='always')

    @api.depends('purchase_cost', 'factory_cost')
    def _compute_total_cost(self):
        for bom in self:
            bom.total_cost = bom.purchase_cost + bom.factory_cost

    # bom模板
    bom_template_id = fields.Many2one('mrp.bom.template', string='BOM模板', track_visibility='always', domain="[('category_ids', 'in', category_id)]")

    @api.onchange('bom_template_id')
    def _onchange_bom_template_id(self):
        if self.bom_template_id:
            self.bom_line = [(5, 0, 0)]
            for line in self.bom_template_id.bom_line:
                self.bom_line = [(0, 0, {
                    'category_id': line.category_id.id
                })]

    # 技术负责人
    technical_user_id = fields.Many2one('res.users', string='技术负责人', track_visibility='always')


class MrpBomLine(models.Model):
    _name = 'mrp.bom.line'
    _description = 'BOM明细'

    # 数量禁止小于等于0
    _sql_constraints = [('product_id_uniq', 'unique(bom_id, product_id)', '明细行产品禁止添加相同产品!'),
                        ('product_qty_check', 'CHECK(product_qty>0)', '数量禁止小于等于0!')
                        ]

    bom_id = fields.Many2one('mrp.bom', string='BOM')
    product_id = fields.Many2one('product.product', string='产品',
                                 domain="[('category_id', '=', category_id)]")
    # 类别
    category_id = fields.Many2one('product.category', string='类别', required=True)
    # 供应商
    supplier_id = fields.Many2one('res.supplier', string='供应商', domain="[('category_ids', 'in', category_id)]")

    # 选择供应商时自动获取价格最低的价格表
    @api.onchange('supplier_id')
    def _onchange_supplier_id(self):
        if self.supplier_id and self.product_id:
            price = self.env['product.price'].search([('product_id', '=', self.product_id.id), ('name', '=', self.supplier_id.id)], order='price', limit=1)
            self.price_id = price.id

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.category_id = self.product_id.category_id.id
            # bom内部禁止添加自身、禁止添加套件
            if self.product_id == self.bom_id.product_id:
                raise UserError(_('BOM内部禁止添加自身!'))
            if self.product_id.bom_id and self.product_id.bom_id.bom_type == 'phantom':
                raise UserError(_('制造BOM禁止添加套件!'))

    sequence = fields.Integer(related='category_id.sequence', string='NO', store=True)
    # 条码
    barcode = fields.Char(string='条码', related='product_id.barcode')
    # 型号
    model = fields.Char(string='型号', related='product_id.model')
    # 图号
    drawing_number = fields.Char(string='图号', related='product_id.drawing_number')
    # 数量
    product_qty = fields.Float(string='数量', default=1)

    # 单位
    uom_id = fields.Many2one('product.uom', string='单位', related='product_id.uom_id')
    note = fields.Text(string='备注')

    # 价格表
    price_id = fields.Many2one('product.price', string='价格来源',
                               domain="[('product_id', '=', product_id), ('name', '=', supplier_id)]")
    # 采购价
    price = fields.Float(string='单价', related='price_id.price')

    # 小计
    subtotal = fields.Float(string='小计', compute='_compute_subtotal')

    @api.depends('product_qty', 'price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.product_qty * line.price

    @api.onchange('price_id')
    def _onchange_price_id(self):
        for line in self:
            line.supplier_id = line.price_id.name.id

    # 记录新增BOM行
    @api.model
    def create(self, vals):
        res = super(MrpBomLine, self).create(vals)
        body = """
                <ul class='text-success'>
                    <li>类型：BOM行新增</li>
                    <li>时间：{}</li>
                    <li>产品：{}</li>
                    <li>数量：{}</li>
                    <li>单价：{}</li>
                </ul>
                """.format(str(fields.Datetime.now()), res.product_id.name, res.product_qty, res.price)
        res.bom_id.message_post(body=Markup(body))
        return res

    # 记录删除BOM行
    def unlink(self):
        for line in self:
            body = """
                    <ul class='text-danger'>
                        <li>类型：BOM行删除</li>
                        <li>时间：{}</li>
                        <li>产品：{}</li>
                        <li>数量：{}</li>
                        <li>单价：{}</li>
                    </ul>
                    """.format(str(fields.Datetime.now()), line.product_id.name, line.product_qty, line.price)
            line.bom_id.message_post(body=Markup(body))
        return super(MrpBomLine, self).unlink()

    # 记录修改BOM行
    def write(self, vals):
        for line in self:
            if 'product_id' in vals:
                new_product_name = self.env['product.product'].browse(vals['product_id']).name
                body = """
                        <ul class='text-success'>
                            <li>类型：BOM行产品变更</li>
                            <li>时间：{}</li>
                            <li>类别：{}</li>
                            <li>原产品：{}</li>
                            <li>新产品：{}</li>
                        </ul>
                        """.format(str(fields.Datetime.now()), line.category_id.name, line.product_id.name, new_product_name)
                line.bom_id.message_post(body=Markup(body))
            if 'product_qty' in vals:
                body = """
                        <ul class='text-success'>
                            <li>类型：BOM行数量变更</li>
                            <li>时间：{}</li>
                            <li>类别：{}</li>
                            <li>产品：{}</li>
                            <li>原数量：{}</li>
                            <li>新数量：{}</li>
                        </ul>
                        """.format(str(fields.Datetime.now()), line.category_id.name, line.product_id.name, line.product_qty, vals['product_qty'])
                line.bom_id.message_post(body=Markup(body))
            if 'price_id' in vals:
                body = """
                        <ul class='text-success'>
                            <li>类型：BOM行价格来源变更</li>
                            <li>时间：{}</li>
                            <li>类别：{}</li>
                            <li>产品：{}</li>
                            <li>原价格来源：{}</li>
                            <li>新价格来源：{}</li>
                        </ul>
                        """.format(str(fields.Datetime.now()), line.category_id.name, line.product_id.name, line.price_id.name, vals['price_id'])
                line.bom_id.message_post(body=Markup(body))
            if 'supplier_id' in vals:
                body = """
                        <ul class='text-success'>
                            <li>类型：BOM行供应商变更</li>
                            <li>时间：{}</li>
                            <li>类别：{}</li>
                            <li>产品：{}</li>
                            <li>原供应商：{}</li>
                            <li>新供应商：{}</li>
                        </ul>
                        """.format(str(fields.Datetime.now()), line.category_id.name, line.product_id.name, line.supplier_id.name, vals['supplier_id'])
                line.bom_id.message_post(body=Markup(body))
            if 'note' in vals:
                body = """
                        <ul class='text-success'>
                            <li>类型：BOM行备注变更</li>
                            <li>时间：{}</li>
                            <li>类别：{}</li>
                            <li>产品：{}</li>
                            <li>原备注：{}</li>
                            <li>新备注：{}</li>
                        </ul>
                        """.format(str(fields.Datetime.now()), line.category_id.name, line.product_id.name, line.note, vals['note'])
                line.bom_id.message_post(body=Markup(body))
        return super(MrpBomLine, self).write(vals)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    bom_id = fields.Many2one('mrp.bom', string='BOM', copy=False, domain="[('product_id', '=', id)]")
