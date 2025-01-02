# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class DeliveryAddress(models.Model):
    _name = 'delivery.address'
    _description = '送货地址'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _sql_constraints = [('name_uniq', 'unique(name)', '送货地址名称必须唯一')]
    name = fields.Char(string='名称', required=True)
    code = fields.Char(string='编码')
    address = fields.Char(string='地址')
    phone = fields.Char(string='电话')
    fax = fields.Char(string='传真')
    email = fields.Char(string='邮箱')
    contact = fields.Char(string='联系人')
    mobile = fields.Char(string='手机')
    note = fields.Text(string='备注')