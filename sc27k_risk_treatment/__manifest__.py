# -*- coding: utf-8 -*-
{
    'name': "Riesgos y Oportunidades - Perfil de Riesgo ISO 27001",
    'summary': "Perfil de tratamiento y aceptación de riesgos de seguridad de la información sobre Riesgos y Oportunidades",
    'description': """
        Extiende matrix.block.line (Riesgos y Oportunidades) con un perfil condicional,
        activo cuando el Identificador es "Seguridad de la información" y el registro es
        un riesgo: activo afectado, amenaza y agente de la amenaza, un flujo de evaluación
        inicial -> tratamiento/controles -> evaluación residual -> aceptación del riesgo,
        y el indicador "Evaluación de Riesgos de Seguridad de la Información" (Impacto x
        Probabilidad, escala 1-25).
    """,
    'author': "Soy Calidad",
    'category': 'iso27001',
    'version': '18.0.1.0.0',
    'depends': [
        'sc27k_base',
        'mgmtsystem_opportunity',
        'mgmtsystem_process_integration',
        'sc27k_asset_inventory',
        'report_xlsx',
    ],
    'data': [
        'data/evaluation_security_information.xml',
        'views/matrix_block_line.xml',
        'report/risk_report.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
