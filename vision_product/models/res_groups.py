# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class UserGroup(models.Model):
    _inherit = 'res.groups'
    _order = 'sequence'

    sequence = fields.Integer('Sequence', default=1000)