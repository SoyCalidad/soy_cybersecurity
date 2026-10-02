{
    'name': 'Adaptation of the context module for the ISO 27001 system',
    'version': '1.0',
    'description': 'Adaptation of the context module for the ISO 27001 system',
    'summary': 'Adaptation of the context module for the ISO 27001 system',
    'author': 'Soy Calidad',
    'website': 'www.soycalidad.com',
    'license': 'Other proprietary',
    'category': 'iso27001',
    'depends': [
        'sc27k_base',
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
