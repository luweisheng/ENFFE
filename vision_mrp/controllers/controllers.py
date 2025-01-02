# -*- coding: utf-8 -*-
# from odoo import http


# class VisionMrp(http.Controller):
#     @http.route('/vision_mrp/vision_mrp', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vision_mrp/vision_mrp/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vision_mrp.listing', {
#             'root': '/vision_mrp/vision_mrp',
#             'objects': http.request.env['vision_mrp.vision_mrp'].search([]),
#         })

#     @http.route('/vision_mrp/vision_mrp/objects/<model("vision_mrp.vision_mrp"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vision_mrp.object', {
#             'object': obj
#         })

