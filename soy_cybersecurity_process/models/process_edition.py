from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProcessEdition(models.Model):
    _inherit = 'process.edition'

    clazz_id = fields.Many2one('documentary.control.clazz', string='Clase', ondelete='set null')
