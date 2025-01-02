# -*- coding: utf-8 -*-
# from odoo import http


# class VisionAccount(http.Controller):
#     @http.route('/vision_account/vision_account', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vision_account/vision_account/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vision_account.listing', {
#             'root': '/vision_account/vision_account',
#             'objects': http.request.env['vision_account.vision_account'].search([]),
#         })

#     @http.route('/vision_account/vision_account/objects/<model("vision_account.vision_account"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vision_account.object', {
#             'object': obj
#         })

