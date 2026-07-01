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


    'depends': [
        'documents',
        'hr_recruitment',


        'mgmtsystem_action',
        'mgmtsystem_nonconformity',
        'website',
        'mgmtsystem_process',
        'hola_calidad',
        'mgmtsystem_documentary_control',
        'mgmtsystem_opportunity',
        'mgmtsystem_infrastructure',

        #'soycalidad_dms',
    ],


    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        "security/ir_rule_data.xml",
        'security/rules.xml',
        'data/evaluation_main_data.xml',
        'data/app_ctrl_data.xml',
        'data/incidents_data.xml',
        'data/data_others.xml',
        'data/dms.xml',
        'data/cybersecurity.clause.csv',
        'data/cybersecurity.diagnostic.requirement.csv',
        'data/cyber_2matrix_block_line.xml',

        'views/controls.xml',
        'views/incidents.xml',
        'views/asset_management.xml',
        'views/app_ctrl_mgmt.xml',
        'views/matrix_view_1.xml',
        'views/matrix_view_2.xml',
        'views/cyber_evaluation.xml',
        'views/diagnostic_views.xml',

        'views/configuration_views_2.xml',
        'views/menus.xml',
        
        'reports/matrix_report.xml',
        'reports/app_ctrl_mgmt_report.xml',
        "static/src/xml/incident.xml",

        #'views/configuration_views.xml',
        #'views/assets.xml',
        #'views/opportunity_onboarding_templates.xml',
        #'report/matrix_report.xml',
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_frontend': [
            '/soy_cybersecurity_cybersecurity/static/src/css/incident.css',
            '/soy_cybersecurity_cybersecurity/static/src/js/incident.js',
        ],
        'web.assets_backend': [
            "soy_cybersecurity_cybersecurity/static/src/login_popup/**/*",
        ]
    } 
}
