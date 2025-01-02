# -*- coding: utf-8 -*-
# from odoo import http


# class VisionPurchase(http.Controller):
#     @http.route('/vision_purchase/vision_purchase', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vision_purchase/vision_purchase/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vision_purchase.listing', {
#             'root': '/vision_purchase/vision_purchase',
#             'objects': http.request.env['vision_purchase.vision_purchase'].search([]),
#         })

#     @http.route('/vision_purchase/vision_purchase/objects/<model("vision_purchase.vision_purchase"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vision_purchase.object', {
#             'object': obj
#         })

