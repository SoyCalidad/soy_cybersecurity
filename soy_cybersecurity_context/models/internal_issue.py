from odoo import api, fields, models

class InternalIssue(models.Model):
    _inherit = 'mgmtsystem.context.internal_issue'

    cybersecurity_scope = fields.Text(string='Alcance del Sistema de Seguridad de la Información')
    quality_policy = fields.Many2many(
        'mgmtsystem.context.policy', string='Política de calidad', domain="[('state','!=','cancel')]")    