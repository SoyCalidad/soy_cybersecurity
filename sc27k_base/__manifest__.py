# -*- coding: utf-8 -*-
{
    'name': "SC27K Base ",
    'summary': "Base module to install the SC 27K modules",
    'description': """
        Adds an identifier in mgmtsystem_context_system for 27K
    """,
    'author': "Soy Calidad",
    'category': 'iso27001',
    'version': '18.0.1.0.0',
    'depends': [ 
        'hola_calidad',
    ],
    'data': [
        'data/mgmtsystem_context_system.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
