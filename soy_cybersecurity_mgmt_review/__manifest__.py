{
    'name': 'Adaptation of the management review module for the ISO 27001 system',
    'version': '1.0',
    'description': 'Adaptation of the management review module for the ISO 27001 system',
    'summary': 'Adaptation of the management review module for the ISO 27001 system',
    'author': 'Soy Calidad',
    'website': 'www.soycalidad.com',
    'license': 'Other proprietary',
    'category': 'iso27001',
    'depends': [
        'mgmtsystem_management_review',
        'mgmtsystem_process_integration',
        
        'soy_cybersecurity_cybersecurity',
    ],
    'data': [
        'views/management_review_views.xml',
        'reports/managementreview_report.xml',
        
        'views/menus.xml',
    ],
    'demo': [
    ],
    'auto_install': False,
    'application': False,
}
