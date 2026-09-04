# -*- coding: utf-8 -*-
{
    'name': "SC27K Base ",
    'summary': "Modulo base para instalar los modulos de SC 27K",
    'description': """
        Agrega un identificador en mgmtsystem_context_system para 27K
    """,
    'author': "Soy Calidad",
    'category': 'iso27001',
    'version': '18.0.1.0.0',
    'depends': [ 
    ],
    'data': [
        'data/mgmtsystem_context_system.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
