# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    # 组件消耗位置
    module_consume_location_id = fields.Many2one('stock.location', string='组件消耗位置', track_visibility='onchange')
    # 成品存放位置
    finished_location_id = fields.Many2one('stock.location', string='成品存放位置', track_visibility='onchange')
    # 虚拟生产车间
    virtual_production_location_id = fields.Many2one('stock.location', string='虚拟生产车间', track_visibility='onchange')