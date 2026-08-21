# -*- coding: utf-8 -*-
from odoo import fields, models


class MgmtsystemAction(models.Model):
    _inherit = 'mgmtsystem.action'

    sc27k_implementation_record = fields.Char(string='Registro de implementación')
