# -*- coding: utf-8 -*-
# from odoo import http


# class VisionSaleStock(http.Controller):
#     @http.route('/vision_sale_stock/vision_sale_stock', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vision_sale_stock/vision_sale_stock/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vision_sale_stock.listing', {
#             'root': '/vision_sale_stock/vision_sale_stock',
#             'objects': http.request.env['vision_sale_stock.vision_sale_stock'].search([]),
#         })

#     @http.route('/vision_sale_stock/vision_sale_stock/objects/<model("vision_sale_stock.vision_sale_stock"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vision_sale_stock.object', {
#             'object': obj
#         })

