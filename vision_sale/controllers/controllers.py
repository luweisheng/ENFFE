# -*- coding: utf-8 -*-
# from odoo import http


# class VisionSale(http.Controller):
#     @http.route('/vision_sale/vision_sale', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vision_sale/vision_sale/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vision_sale.listing', {
#             'root': '/vision_sale/vision_sale',
#             'objects': http.request.env['vision_sale.vision_sale'].search([]),
#         })

#     @http.route('/vision_sale/vision_sale/objects/<model("vision_sale.vision_sale"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vision_sale.object', {
#             'object': obj
#         })

