# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductionFactory(models.Model):
    _name = 'production.factory'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '工厂'

    _sql_constraints = [('name_uniq', 'unique(name)', '工厂名称必须唯一')]
    name = fields.Char(string='名称', required=True)
    # 负责人
    manager_id = fields.Many2one('res.users', string='负责人')
    code = fields.Char(string='编码')
    address = fields.Char(string='地址')
    phone = fields.Char(string='电话')
    fax = fields.Char(string='传真')
    email = fields.Char(string='邮箱')
    contact = fields.Char(string='联系人')
    mobile = fields.Char(string='手机')
    note = fields.Text(string='备注')