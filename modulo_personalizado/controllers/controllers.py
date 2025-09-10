# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class ModuloPersonalizado(http.Controller):

    @http.route('/modulo_personalizado/modulo_personalizado', auth='public', website=True)
    def index(self, **kw):
        return "Hola, mundo"

    @http.route('/modulo_personalizado/modulo_personalizado/objects', auth='public', website=True)
    def list(self, **kw):
        objects = request.env['modulo_personalizado.modulo_personalizado'].sudo().search([])
        return request.render('modulo_personalizado.listing', {
            'root': '/modulo_personalizado/modulo_personalizado',
            'objects': objects,
        })

    @http.route('/modulo_personalizado/modulo_personalizado/objects/<model("modulo_personalizado.modulo_personalizado"):obj>', auth='public', website=True)
    def object(self, obj, **kw):
        return request.render('modulo_personalizado.object', {'object': obj})
