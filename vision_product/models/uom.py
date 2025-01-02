# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductUom(models.Model):
    _name = 'product.uom'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '单位'

    _sql_constraints = [('name_uniq', 'unique(name)', '单位名称禁止重复!')]
    name = fields.Char(string='名称')
