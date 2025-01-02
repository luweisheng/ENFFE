# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCorporation(models.Model):
    _name = 'res.corporation'
    _description = '客户'

    name = fields.Char(string='名称', required=True)
    # 编码
    code = fields.Char(string='编码')
    address = fields.Char(string='地址')
    phone = fields.Char(string='电话')
    email = fields.Char(string='邮箱')
    # 税率
    tax_rate = fields.Float(string='税率')