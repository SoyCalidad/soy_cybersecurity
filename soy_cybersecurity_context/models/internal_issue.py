from odoo import api, fields, models

class InternalIssue(models.Model):
    _inherit = 'mgmtsystem.context.internal_issue'

    cybersecurity_scope = fields.Text(string='Scope of the Information Security System')
    quality_policy = fields.Many2many(
        'mgmtsystem.context.policy', string='Quality policy', domain="[('state','!=','cancel')]")    