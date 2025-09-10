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
    
    #use of ia
    use_ia_object = fields.Text(string="Objeto")
    use_ia_scope = fields.Text(string="Alcance")
    use_ia_role = fields.Html(string="Roles y responsabilidades")
    use_ia_individual_res = fields.Text(string="Responsabilidad individual")
    use_ia_confidentiality = fields.Text(string="Confidencialidad")
    use_ia_ethical_use = fields.Text(string="Uso ético")
    use_ia_luc = fields.Text(string="Limitación de casos de uso")
    use_ia_cons_biase = fields.Text(string="Consideración de sesgos")
    use_ia_riptp = fields.Text(string="Respeto a la propiedad intelectual de terceros")
    use_ia_respect_human = fields.Text(string="Principio de respeto al ser humano y al bienestar social")
    use_ia_review_ci = fields.Text(string="Revisión y mejora continua")
    
    #save_dev
    save_dev_objective = fields.Text(string="Objetivo")
    save_dev_scope = fields.Text(string="Alcance")
    save_dev_role = fields.Html(string="Roles y Responsabilidades")
    save_dev_principle = fields.Html(string="Principios de desarrollo seguro")
    save_dev_life_cycle = fields.Html(string="Ciclo de Vida de Desarrollo Seguro")
    save_dev_training = fields.Text(string="Capacitación y Concienciación")
    save_dev_review_compliance = fields.Text(string="Revisión y Cumplimiento")



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
    
    #use of ia
    use_ia_object = fields.Text(string="Objeto")
    use_ia_scope = fields.Text(string="Alcance")
    use_ia_role = fields.Html(string="Roles y responsabilidades")
    use_ia_individual_res = fields.Text(string="Responsabilidad individual")
    use_ia_confidentiality = fields.Text(string="Confidencialidad")
    use_ia_ethical_use = fields.Text(string="Uso ético")
    use_ia_luc = fields.Text(string="Limitación de casos de uso")
    use_ia_cons_biase = fields.Text(string="Consideración de sesgos")
    use_ia_riptp = fields.Text(string="Respeto a la propiedad intelectual de terceros")
    use_ia_respect_human = fields.Text(string="Principio de respeto al ser humano y al bienestar social")
    use_ia_review_ci = fields.Text(string="Revisión y mejora continua")
    
    #save_dev
    save_dev_objective = fields.Text(string="Objetivo")
    save_dev_scope = fields.Text(string="Alcance")
    save_dev_role = fields.Html(string="Roles y Responsabilidades")
    save_dev_principle = fields.Html(string="Principios de desarrollo seguro")
    save_dev_life_cycle = fields.Html(string="Ciclo de Vida de Desarrollo Seguro")
    save_dev_training = fields.Text(string="Capacitación y Concienciación")
    save_dev_review_compliance = fields.Text(string="Revisión y Cumplimiento")
    
    @api.depends("system_id")
    def _compute_is_specific_policy_system(self):
        super()._compute_is_specific_policy_system()
        policy_use_ia = self.env.ref('soy_cybersecurity_context.policy_system_use_ia')
        policy_safe_dev = self.env.ref('soy_cybersecurity_context.policy_system_safe_dev')
        for record in self:
            record.is_policy_system_save_dev = record.system_id == policy_safe_dev
            record.is_policy_system_use_ia = record.system_id == policy_use_ia

    is_policy_system_save_dev = fields.Boolean(compute="_compute_is_specific_policy_system")
    is_policy_system_use_ia = fields.Boolean(compute="_compute_is_specific_policy_system")

    #on change plantilla
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
        
        self.use_ia_object = self.template_.use_ia_object
        self.use_ia_scope = self.template_.use_ia_scope
        self.use_ia_role = self.template_.use_ia_role
        self.use_ia_individual_res = self.template_.use_ia_individual_res
        self.use_ia_confidentiality = self.template_.use_ia_confidentiality
        self.use_ia_ethical_use = self.template_.use_ia_ethical_use
        self.use_ia_luc = self.template_.use_ia_luc
        self.use_ia_cons_biase = self.template_.use_ia_cons_biase
        self.use_ia_riptp = self.template_.use_ia_riptp
        self.use_ia_respect_human = self.template_.use_ia_respect_human
        self.use_ia_review_ci = self.template_.use_ia_review_ci 
        
        #save_dev
        self.save_dev_objective = self.template_.save_dev_objective 
        self.save_dev_scope = self.template_.save_dev_scope 
        self.save_dev_role = self.template_.save_dev_role 
        self.save_dev_principle = self.template_.save_dev_principle 
        self.save_dev_life_cycle = self.template_.save_dev_life_cycle
        self.save_dev_training = self.template_.save_dev_training
        self.save_dev_review_compliance = self.template_.save_dev_review_compliance