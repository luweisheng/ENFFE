# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # 产品生成器
    builder_id = fields.Many2one('vision.product.builder', string='产品模板')

    builder_line_ids = fields.One2many('vision.product.template.property', 'product_id', string='产品属性列表')

    # 名称，条码唯一限制
    _sql_constraints = [('name_uniq', 'unique(name)', '名称禁止重复!'),
                        ('barcode_uniq', 'unique(barcode)', '条码禁止重复!')]


    @api.onchange('builder_line_ids')
    def _set_product_name(self):
        for line in self:
            if line.categ_id:
                name = ''
                category_code = line.categ_id.code
                if not category_code:
                    raise UserError(_('请先设置产品类别编码'))
                barcode = ''
                for value in line.builder_line_ids:
                    if value.property_value_id:
                        if value.show_name:
                            name += value.property_id.name + '：'
                        name += value.property_value_id.name + value.sep_value
                        code = value.code
                        if code:
                            barcode += code

                serial_number_length = line.categ_id.barcode_length - len(barcode) - len(category_code)
                # 获取该生成器的产品数量
                product_count = self.env['product.template'].search_count([('builder_id', '=', line.builder_id.id)])
                barcode = category_code + barcode
                barcode += str(product_count + 1).zfill(serial_number_length)
                if name:
                    new_name = name[:-1]
                    data = {'name': new_name, 'display_name': new_name, 'barcode': barcode}
                    line.update(data)
                line.builder_id.current_number = barcode
            else:
                line.builder_id.current_number = ''

    # @api.onchange('builder_id')
    # def _onchange_builder_id(self):
    #     builder_id = self.builder_id
    #     # 如果builder_id为真，并且不等于原来的builder_id
    #     if builder_id:
    #         self.builder_line_ids = None
    #         builder_line_ids = []
    #         # 更新产品属性列表
    #         for line in builder_id.builder_line_ids:
    #                 builder_line_ids.append((0, 0, {
    #                     'property_id': line.property_id.id,
    #                     'hide_from_customer': line.hide_from_customer,
    #                     'hide_from_supplier': line.hide_from_supplier,
    #                     'required': line.required,
    #                     'participate_code': line.participate_code,
    #                     'show_name': line.show_name,
    #                 }))
    #         self.builder_line_ids = builder_line_ids

    # 当产品有采购销售时，禁止修改产品属性列表
    @api.onchange('sales_count', 'purchased_product_qty')
    def _onchange_sales_purchase_count(self):
        for line in self:
            if line.sales_count > 0 or line.purchased_product_qty > 0:
                raise UserError(_('产品已有采购或销售记录，不能修改产品属性列表'))

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        res = super(ProductTemplate, self).copy({'name': self.name + '(复制)'})
        return res



