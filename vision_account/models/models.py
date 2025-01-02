# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class vision_account(models.Model):
#     _name = 'vision_account.vision_account'
#     _description = 'vision_account.vision_account'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

