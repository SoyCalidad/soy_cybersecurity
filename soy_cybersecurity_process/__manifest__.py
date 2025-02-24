{
    'name': 'Adecución del módulo de procesos para el sistema ISO 27001',
    'version': '1.0',
    'description': 'Adecución del módulo de procesos para el sistema ISO 27001',
    'summary': 'Adecución del módulo de procesos para el sistema ISO 27001',
    'author': 'Soy Calidad',
    'website': 'www.soycalidad.com',
    'license': 'Other proprietary',
    'category': 'iso27001',
    'depends': [
        'mgmtsystem_process',
        'mgmtsystem_process_integration',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/documentary_control_views.xml',
        'views/process_edition_views.xml',
        'views/menus.xml',
        'report/report_process_edition.xml',
        'data/data.xml',
    ],
    'demo': [
    ],
    'auto_install': False,
    'application': False,
}
