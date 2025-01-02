# -*- coding: utf-8 -*-
# from odoo import http


# class VisionStock(http.Controller):
#     @http.route('/vision_stock/vision_stock', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vision_stock/vision_stock/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vision_stock.listing', {
#             'root': '/vision_stock/vision_stock',
#             'objects': http.request.env['vision_stock.vision_stock'].search([]),
#         })

#     @http.route('/vision_stock/vision_stock/objects/<model("vision_stock.vision_stock"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vision_stock.object', {
#             'object': obj
#         })

