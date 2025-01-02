# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    # 限制产品修改内容
    product_edit_ids = fields.Many2many('ir.model.fields',
                                        string='禁止修改字段',
                                        domain="[('model', '=', 'product.product')]",
                                        default=lambda self: self.env['ir.model.fields'].search([('model', '=', 'product.product'), ('name', '=', 'name')]).ids)