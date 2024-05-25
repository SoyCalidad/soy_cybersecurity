# -*- coding: utf-8 -*-
{
    'name': "Gestión de Seguridad de la Información",

    'summary': """
        Gestión de Seguridad de la Información""",

    'description': """
        [Descripción]
    """,

    'author': "Soy Calidad",


    'category': 'iso27001',
    'version': '0.1',


    'depends': ['mgmtsystem_action',
                'mgmtsystem_process',
                'hola_calidad',
                'mgmtsystem_documentary_control', ],


    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/rules.xml',
        'data/evaluation_main_data.xml',
        'data/data_others.xml',
        'views/menus.xml',
        'views/block_views.xml',
        'views/matrix_views.xml',
        'views/configuration_views_2.xml',
        #'views/configuration_views.xml',
        #'views/assets.xml',
        #'views/opportunity_onboarding_templates.xml',
        #'report/matrix_report.xml',
    ],
    'installable': True,
    'application': True,    
}
