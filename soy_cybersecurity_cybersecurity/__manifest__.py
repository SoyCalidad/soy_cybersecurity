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
        'data/app_ctrl_data.xml',
        'data/data_others.xml',
        'views/menus.xml',
        'views/asset_management.xml',
        'views/app_ctrl_mgmt.xml',
        'views/matrix_view_1.xml',
        'views/matrix_view_2.xml',
        
        'views/configuration_views_2.xml',
        'reports/matrix_report.xml',
        'reports/app_ctrl_mgmt_report.xml',

        #'views/configuration_views.xml',
        #'views/assets.xml',
        #'views/opportunity_onboarding_templates.xml',
        #'report/matrix_report.xml',
    ],
    'installable': True,
    'application': True,    
}
