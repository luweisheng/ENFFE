# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_quantity = fields.Float(string='现有量', compute='_compute_product_quantity')

    @api.model
    def _compute_product_quantity(self):
        for product in self:
            product.product_quantity = self.env['stock.quantity'].search_count([('product_id', '=', product.id),
                                                                                ('location_id.location_type', '=',
                                                                                 'internal')])

    def action_open_quantity_tree_view(self):
        action = self.env.ref('vision_stock.action_stock_quantity_report').read()[0]
        action['domain'] = [('product_id', '=', self.id)]
        return action


