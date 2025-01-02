# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class vision_promise_group(models.Model):
#     _name = 'vision_promise_group.vision_promise_group'
#     _description = 'vision_promise_group.vision_promise_group'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
