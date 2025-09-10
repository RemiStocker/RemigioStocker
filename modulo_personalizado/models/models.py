# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ModuloPersonalizado(models.Model):
    _name = 'modulo_personalizado.modulo_personalizado'
    _description = 'Módulo Personalizado - Ejemplo'

    name = fields.Char(string="Nombre")
    value = fields.Integer(string="Valor", default=0)
    value2 = fields.Float(string="Valor %", compute="_compute_value2", store=True)
    description = fields.Text(string="Descripción")

    @api.depends('value')
    def _compute_value2(self):
        for record in self:
            record.value2 = float(record.value or 0) / 100.0
