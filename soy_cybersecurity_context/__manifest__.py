{
    'name': 'Adecución del módulo de contexto para el sistema ISO 27001',
    'version': '1.0',
    'description': 'Adecución del módulo de contexto para el sistema ISO 27001',
    'summary': 'Adecución del módulo de contexto para el sistema ISO 27001',
    'author': 'Soy Calidad',
    'website': 'www.soycalidad.com',
    'license': 'Other proprietary',
    'category': 'iso27001',
    'depends': [
        'mgmtsystem_process',
        'mgmtsystem_context',
        'mgmtsystem_process_integration',
    ],
    'data': [
        'data/policy_template_data.xml',
        'views/internal_issue.xml',
        'views/policy_template.xml',
        'reports/policy.xml',
        'reports/internal_issue.xml',
        
        
    ],
    'demo': [
    ],
    'auto_install': False,
    'application': False,
}
