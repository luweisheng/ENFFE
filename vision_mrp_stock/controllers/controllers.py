# -*- coding: utf-8 -*-
# from odoo import http


# class VisionMrpStock(http.Controller):
#     @http.route('/vision_mrp_stock/vision_mrp_stock', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vision_mrp_stock/vision_mrp_stock/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vision_mrp_stock.listing', {
#             'root': '/vision_mrp_stock/vision_mrp_stock',
#             'objects': http.request.env['vision_mrp_stock.vision_mrp_stock'].search([]),
#         })

#     @http.route('/vision_mrp_stock/vision_mrp_stock/objects/<model("vision_mrp_stock.vision_mrp_stock"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vision_mrp_stock.object', {
#             'object': obj
#         })

