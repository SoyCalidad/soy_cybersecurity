# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class ManagementReview(models.Model):
    _inherit = 'management.review'


    it_security_target = fields.Html( 
        string='Objetivo de seguridad de la información',
        store=True,)
    
    it_security_target_description = fields.Text( string='Interpretación')

    it_legal_requirements = fields.Html( 
        string='Requerimientos legales y otros requerimientos',
        store=True,)
    
    it_legal_requirements_description = fields.Text( string='Interpretación')

    # G. COMUNICACIONES PERTINENTES CON LAS PARTES INTERESADAS

    it_comunication_plan_ids = fields.Many2many(
        'comunication.plan.line', string='Planes de Comunicación')
    it_comunication_plan = fields.Html('Comunicaciones')
    it_comunication_plan_interpretation = fields.Text(
        'Interpretación de las comunicaciones')
