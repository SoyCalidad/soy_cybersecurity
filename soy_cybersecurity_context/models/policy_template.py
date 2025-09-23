from odoo import api, fields, models

import logging 


_logger = logging.getLogger(__name__)

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
        if not self.template_:
            return
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
        

    @api.model
    def default_get(self, fields_list):
        """ Sobrescribe valores por defecto al abrir el formulario """
        res = super().default_get(fields_list)

        if "save_dev_objective" in fields_list:
            res["save_dev_objective"] = "Esta política establece reglas básicas para garantizar la seguridad en el desarrollo, adquisición y mantenimiento de aplicaciones y sistemas, en cumplimiento con la ISO/IEC 27001:2022."
            
        if "save_dev_scope" in fields_list:
            res["save_dev_scope"] = "Aplica para todos los desarrollos de software, ya sean realizados internamente, a través de terceros o adquiridos a proveedores. También se extiende al personal encargado de la operación, mantenimiento y soporte de los productos de software utilizados para la prestación de servicios, garantizando que se integren los requisitos de seguridad en todas las etapas del ciclo de vida del desarrollo."
        res["save_dev_role"] = """
        <p><b>CEO<b>: Aprobar y supervisar la política.</p>
        <p><b>COO</b>: Garantizar que en los procesos de soporte se incluya prácticas de desarrollo seguro de software.</p>
        <p><b>CTO/CIO</b>:                     
        Implementar&nbsp;prácticas de desarrollo seguro en todo el ciclo de vida 
        del software.&nbsp;y coordinar pruebas de seguridad.</p>
        <p><b>Proveedores</b>:
        Cumplir con los requisitos de seguridad definidos en contratos.</p><p> """
        res["save_dev_principle"] = """
         <p>La organización establece los siguientes principios  generales de seguridad para todo el ciclo de vida del desarrollo de software:</p>
         <ul>
            <li>
            <b>Seguridad por diseño y por defecto</b>: Los sistemas y aplicaciones deben concebirse  considerando la seguridad desde la fase inicial, aplicando configuraciones  seguras por defecto.
            </li>                                                  
            <li>
            <b>Principio de menor privilegio</b>: Los accesos y permisos deben limitarse    estrictamente a lo necesario para cada función.
            </li>                       
            <li>
            <b>Defensa en profundidad</b>: Se aplicarán controles de seguridad en múltiples capas para reducir el riesgo de vulnerabilidades explotables.
            </li>               
            <li>
            <b>Economía  de mecanismos:&nbsp;</b>Se priorizan soluciones simples,&nbsp;eficientes y necesarias según el riesgo al que está expuesto el activo, reduciendo la superficie de ataque y facilitando el mantenimiento.
            </li>                  
            <li>
            <b>Segregación de funciones y entornos</b>: Las funciones críticas y los entornos (desarrollo, pruebas y producción) deben estar claramente separados para prevenir accesos indebidos.
            </li>                                           
            <li>
            <b>Minimización de la superficie de ataque</b>: Se deben eliminar funciones innecesarias y deshabilitar servicios que no sean requeridos.
            </li>                        
            <li>
            <b>Gestión de vulnerabilidades</b>: Las vulnerabilidades deben ser identificadas, registradas y corregidas oportunamente, en cualquier fase del ciclo de vida.
            </li>                                                                 
            <li>
            <b>Usabilidad centrada en el usuario:&nbsp;</b>Los mecanismos de seguridad se diseñan para ser intuitivos y no interferir con el uso legítimo.
            </li>              
            <li>
            <b>Fallo en estado seguro:&nbsp;</b>Ante errores o fallos imprevistos el sistema  debe responder de forma segura y contar con un estado fijo conocido.
            </li>  
            <li>
            <b>Cumplimiento normativo</b>: El desarrollo debe alinearse con la ISO/IEC 27001:2022 y regulaciones aplicables.
            </li>                                              
        </ul>
        <p> 
    
        </p>
        """
        res["save_dev_life_cycle"] = """
         <p>Se contempla las siguientes fases según el ciclo de desarrollo seguro de software:</p>
         <p><b>Planificación: </b>Se deben identificar y documentar los 
            requisitos de seguridad antes de iniciar el desarrollo o adquirir software. Es obligatorio establecer principios generales de seguridad en el ciclo de vida, como la seguridad por diseño, el principio de menor privilegio y la  minimización de la superficie de ataque, de acuerdo con los resultados de un   
            análisis de riesgos.</p>
<p><b>Desarrollo: </b>Durante esta fase se aplican guías de              
codificación segura reconocidas, como OWASP Top 10 y CWE. El código debe       
someterse a revisiones mediante análisis entre pares o herramientas            
automáticas, según corresponda a la criticidad del desarrollo. Todos los cambios                 
deben registrarse en un sistema de control de versiones, asegurando que cada   
modificación sea revisada, aprobada y debidamente documentada antes de su      
despliegue.</p><p><b>Pruebas: </b>Es obligatorio realizar pruebas de seguridad 
antes de la liberación del software, incluyendo análisis estáticos, dinámicos, 
manuales y pruebas funcionales. Debe validarse que no existan vulnerabilidades 
críticas y que todos los datos de prueba utilizados sean ficticios,            
anonimizados o sintéticos, evitando el uso de datos reales de clientes para    
prevenir la exposición de información sensible en entornos de desarrollo y     
pruebas. </p><p><b>Despliegue: </b>Los entornos de desarrollo, pruebas y       
producción deben mantenerse completamente separados y protegidos, garantizando 
que solo personal autorizado pueda acceder a cada uno de ellos. En proyectos   
externalizados, se debe asegurar que los proveedores cumplan con las cláusulas 
de seguridad establecidas en los contratos. Antes de pasar cualquier desarrollo
a producción, deben aplicarse los procedimientos formales de gestión de cambios
y contar con la aprobación correspondiente.</p><p><b>Mantenimiento: </b>Todas las vulnerabilidades detectadas+
deben ser gestionadas mediante la aplicación de parches, actualizaciones o     
correcciones en el menor tiempo posible, priorizando según su nivel de         
criticidad. Los hallazgos de seguridad deben registrarse en un sistema de      
seguimiento, documentando su tratamiento hasta su resolución. Además, se debe  
realizar de manera periódica una revisión de la seguridad de los sistemas en   
operación, asegurando que se mantengan alineados con los requisitos y controles
establecidos.</p><p> 
        """
        
        res["save_dev_training"] = "El personal técnico debe recibir formación básica en desarrollo seguro y actualización periódica en buenas prácticas según el plan de capacitaciones de la empresa, con el fin de garantizar que las medidas de seguridad sean implementadas de manera efectiva."
        res["save_dev_review_compliance"] = "La política será revisada al menos una vez al año o cuando existan cambios significativos en el entorno tecnológico, normativo o de amenazas. El cumplimiento será verificado mediante auditorías y revisiones internas, y cualquier desviación deberá ser corregida mediante un plan de acción."
        
        res["use_ia_object"] = "El objeto de esta política es establecer un marco de principios y directrices que aseguren que el uso y gestión de la inteligencia artificial en la organización se realice de manera ética, segura y transparente, en cumplimiento de la normativa vigente, protegiendo los derechos de las personas y promoviendo la confianza."
        res["use_ia_scope"] = "Esta política aplica a todo sistema de IA desarrollado, adquirido o utilizado por la organización y a todo empleado o proveedor que interactúe con dichos sistemas, según sea el caso."
        res["use_ia_role"] = """
            <p><b>CEO</b>:                                                                   
Aprobar,&nbsp;supervisar la política y los casos de uso de alto riesgo.</p><p><b>Trabajadores
de AIVORA:&nbsp; </b>Usar las herramientas de forma responsable, siguiendo  
la política y reportando incidentes, errores o impactos no previstos.</p><p><b>Proveedores</b>:
cumplir con los requisitos de seguridad definidos en contratos.</p><p>      
</p>
        """
        res["use_ia_individual_res"] = "Los trabajadores son responsables de la calidad, veracidad y autoría de su trabajo. La IA se emplea únicamente como herramienta de apoyo y no sustituye la responsabilidad profesional."
        res["use_ia_confidentiality"] = "No se permite introducir en sistemas de IA datos sensibles, personales o confidenciales de la organización, salvo que se trate de entornos autorizados y controlados."
        res["use_ia_ethical_use"] = "Está prohibido usar IA para generar contenidos que vulneren derechos de autor, promuevan discriminación, difundan información falsa o dañen la reputación de la organización."
        res["use_ia_luc"] = "La IA no puede emplearse en procesos de toma de decisiones automatizadas que afecten a personas (como contratación, evaluaciones de desempeño o asignación de beneficios) sin aprobación expresa de la Dirección y cumplimiento normativo."
        res["use_ia_cons_biase"] = "Los trabajadores deben ser conscientes de que los sistemas de IA pueden reflejar sesgos en los datos de entrenamiento. Es obligatorio revisar y validar los resultados para identificar posibles sesgos y, cuando sea necesario, aplicar medidas de corrección o reportar incidencias."
        res["use_ia_riptp"] = "Está prohibido introducir en la IA información o contenidos que vulneren derechos de autor, marcas registradas u otros derechos de propiedad intelectual. El personal debe asegurarse de que el uso de IA respete las licencias y normativas aplicables."
        res["use_ia_respect_human"] = "La IA debe utilizarse únicamente como herramienta al servicio de las personas, favoreciendo la equidad, la inclusión y el bienestar social. No se permitirá su uso en actividades que puedan causar daño, discriminación o vulneración de la dignidad humana."
        res["use_ia_review_ci"] = "Revisar la política anualmente o ante cambios en la tecnología y/o de la normativa vigente."
        
        return res
    
    