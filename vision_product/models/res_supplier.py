# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


# 付款条款
class ResPaymentTerm(models.Model):
    _name = 'res.payment.term'
    _description = '付款条款'

    name = fields.Char(string='名称', required=True)
    code = fields.Char(string='编码')
    note = fields.Text(string='备注')


# 贸易条款
class ResTradeTerm(models.Model):
    _name = 'res.trade.term'
    _description = '贸易条款'

    name = fields.Char(string='名称', required=True)
    code = fields.Char(string='编码')
    note = fields.Text(string='备注')


class ResSupplier(models.Model):
    _name = 'res.supplier'
    _description = '供应商'

    name = fields.Char(string='名称', required=True)
    # 付款条款
    payment_term_id = fields.Many2one('res.payment.term', string='付款条款', track_visibility='always')
    # 贸易条款
    trade_term_id = fields.Many2one('res.trade.term', string='贸易条款', track_visibility='always')
    # 采购员
    user_id = fields.Many2one('res.users', string='采购员', track_visibility='always')
    code = fields.Char(string='编码')
    address = fields.Char(string='地址')
    phone = fields.Char(string='电话')
    fax = fields.Char(string='传真')
    email = fields.Char(string='邮箱')
    contact = fields.Char(string='联系人')
    mobile = fields.Char(string='手机')
    note = fields.Text(string='备注')
    # 供货品类
    category_ids = fields.Many2many('product.category', string='供货品类')
    # 含税
    tax_included = fields.Boolean(string='含税')
    # 税率
    tax_rate = fields.Float(string='税率')