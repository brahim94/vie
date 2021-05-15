# -*- coding: utf-8 -*-
# from odoo import http


# class TechAccesright(http.Controller):
#     @http.route('/tech_accesright/tech_accesright/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tech_accesright/tech_accesright/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tech_accesright.listing', {
#             'root': '/tech_accesright/tech_accesright',
#             'objects': http.request.env['tech_accesright.tech_accesright'].search([]),
#         })

#     @http.route('/tech_accesright/tech_accesright/objects/<model("tech_accesright.tech_accesright"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tech_accesright.object', {
#             'object': obj
#         })
