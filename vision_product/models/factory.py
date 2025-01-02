# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VisionFactor(models.Model):
    _name = 'vision.factor'
    _description = 'Factor'

    name = fields.Char(string='工厂名称', required=True)
    # 工厂负责人
    manager_id = fields.Many2one('res.users', string='工厂负责人')
    code = fields.Char(string='编码')
    note = fields.Text(string='备注')