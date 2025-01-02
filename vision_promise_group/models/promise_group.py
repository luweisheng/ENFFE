# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    vision_users_group_id = fields.Many2one('vision.users.group', string="用户权限组")


class ResCompany(models.Model):
    _inherit = 'res.company'

    vision_company_group_id = fields.Many2one('vision.company.group', string="公司权限组")


class VisionCompanyGroup(models.Model):
    _name = "vision.company.group"
    _description = "公司中间表"

    name = fields.Char('名称')


class VisionUserGroup(models.Model):
    _name = "vision.users.group"
    _description = "用户中间表"

    name = fields.Char('名称')

