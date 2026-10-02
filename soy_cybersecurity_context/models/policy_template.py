from odoo import api, fields, models

class PolicyTemplate(models.Model):
    _inherit = 'mgmtsystem.context.policy.template'

    cyber_organization_context = fields.Text(string='Context of the organization')
    cyber_direction_help = fields.Text(string='Management support')
    
    cyber_risk_handling = fields.Text(string='Risk assessment and treatment') #new
    cyber_legal_req = fields.Text(string='Legal Requirements')
    cyber_responsibility_assignment = fields.Text(string='Assignment of responsibilities') #new

    cyber_standard_commitment = fields.Text(string='Commitment to the requirements of the standard')
    cyber_staff_participation = fields.Text(string='Staff participation')
    cyber_continuous_improvement = fields.Text(string='Continual Improvement')

    cyber_control_implementation = fields.Text(string='Implementation of controls') #new
    cyber_security_goals = fields.Text(string='Information security objectives') #new



class Policy(models.Model):
    _inherit = 'mgmtsystem.context.policy'

    cyber_organization_context = fields.Text(string='Context of the organization')
    cyber_direction_help = fields.Text(string='Management support')

    cyber_risk_handling = fields.Text(string='Risk assessment and treatment') #new
    cyber_legal_req = fields.Text(string='Legal Requirements')
    cyber_responsibility_assignment = fields.Text(string='Assignment of responsibilities') #new

    cyber_standard_commitment = fields.Text(string='Commitment to the requirements of the standard')
    cyber_staff_participation = fields.Text(string='Staff participation')
    cyber_continuous_improvement = fields.Text(string='Continual Improvement')

    cyber_control_implementation = fields.Text(string='Implementation of controls') #new
    cyber_security_goals = fields.Text(string='Information security objectives') #new

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