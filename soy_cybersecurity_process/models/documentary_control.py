from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DocumentaryControlClazz(models.Model):
    _name = 'documentary.control.clazz'
    _description = 'Master list class'

    name = fields.Char('Name')


class DocumentaryControl(models.Model):
    _inherit = 'documentary.control'

    clazz_id = fields.Many2one('documentary.control.clazz', string='Class', ondelete='set null')
