# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BatchCreateProducts(models.TransientModel):
    _name = 'batch.create.products'
    _description = '批量创建产品'

    category_id = fields.Many2one('product.category', string='类别', required=True)
    # 类别属性
    builder_line_ids = fields.One2many('vision.product.property', 'category_id', string='属性')

