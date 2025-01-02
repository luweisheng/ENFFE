# -*- coding: utf-8 -*-
# from odoo import http


# class visionPromiseGroup(http.Controller):
#     @http.route('/vision_promise_group/vision_promise_group/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vision_promise_group/vision_promise_group/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vision_promise_group.listing', {
#             'root': '/vision_promise_group/vision_promise_group',
#             'objects': http.request.env['vision_promise_group.vision_promise_group'].search([]),
#         })

#     @http.route('/vision_promise_group/vision_promise_group/objects/<model("vision_promise_group.vision_promise_group"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vision_promise_group.object', {
#             'object': obj
#         })
