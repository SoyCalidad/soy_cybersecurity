from odoo import api, fields, models

class PolicyTemplate(models.Model):
    _inherit = 'mgmtsystem.context.policy.template'

    cyber_organization_context = fields.Text(string='Contexto de la organización')
    cyber_direction_help = fields.Text(string='Apoyo para la dirección')
    
    cyber_risk_handling = fields.Text(string='Evaluación y tratamiento de riesgos') #new
    cyber_legal_req = fields.Text(string='Requisitos Legales')
    cyber_responsibility_assignment = fields.Text(string='Asignación de responsabilidades') #new

    cyber_standard_commitment = fields.Text(string='Compromiso para los requisitos de la norma')
    cyber_staff_participation = fields.Text(string='Participación del personal')
    cyber_continuous_improvement = fields.Text(string='Mejora Continua')

    cyber_control_implementation = fields.Text(string='Implementación de controles') #new
    cyber_security_goals = fields.Text(string='Objetivos para la seguridad de la información') #new



class Policy(models.Model):
    _inherit = 'mgmtsystem.context.policy'

    cyber_organization_context = fields.Text(string='Contexto de la organización')
    cyber_direction_help = fields.Text(string='Apoyo para la dirección')

    cyber_risk_handling = fields.Text(string='Evaluación y tratamiento de riesgos') #new
    cyber_legal_req = fields.Text(string='Requisitos Legales')
    cyber_responsibility_assignment = fields.Text(string='Asignación de responsbilidades') #new

    cyber_standard_commitment = fields.Text(string='Compromiso para los requisitos de la norma')
    cyber_staff_participation = fields.Text(string='Participación del personal')
    cyber_continuous_improvement = fields.Text(string='Mejora Continua')

    cyber_control_implementation = fields.Text(string='Implementación de controles') #new
    cyber_security_goals = fields.Text(string='Objetivos para la seguridad de la información') #new

    @api.onchange('template_')
    def _onchange_template_(self):
        super()._onchange_template_()
        self.name = self.template_.name
        self.cyber_organization_context = self.template_.cyber_organization_context
        self.cyber_direction_help = self.template_.cyber_direction_help

        self.cyber_risk_handling = self.template_.cyber_risk_handling
        self.cyber_legal_req = self.template_.cyber_legal_req
        self.cyber_responsibility_assignment = self.template_.cyber_responsibility_assignment

        
        self.cyber_standard_commitment = self.template_.cyber_standard_commitment
        self.cyber_staff_participation = self.template_.cyber_staff_participation
        self.cyber_continuous_improvement = self.template_.cyber_continuous_improvement

        self.cyber_control_implementation = self.template_.cyber_control_implementation
        self.cyber_security_goals = self.template_.cyber_security_goals