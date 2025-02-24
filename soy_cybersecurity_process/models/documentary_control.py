from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DocumentaryControlClazz(models.Model):
    _name = 'documentary.control.clazz'
    _description = 'Clase de Lista maestra'

    name = fields.Char('Nombre')


class DocumentaryControl(models.Model):
    _inherit = 'documentary.control'

    clazz_id = fields.Many2one('documentary.control.clazz', string='Clase')
