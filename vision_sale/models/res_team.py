# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResTeam(models.Model):
    _name = 'res.team'
    _description = '销售团队'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _sql_constraints = [('name_uniq', 'unique(name)', '销售团队名称必须唯一')]
    name = fields.Char(string='名称', required=True)
    code = fields.Char(string='编码')
    note = fields.Text(string='备注')
    user_ids = fields.Many2many('res.users', 'team_user_ids', string='销售员')
    manager_id = fields.Many2one('res.users', string='销售经理')
    member_count = fields.Integer(string='成员数', compute='_compute_member_count')

    @api.depends('user_ids')
    def _compute_member_count(self):
        for team in self:
            team.member_count = len(team.user_ids)
