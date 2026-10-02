# -*- coding: utf-8 -*-
{
    'name': "Risks and Opportunities - ISO 27001 Risk Profile",
    'summary': "Treatment and acceptance profile for information security risks on top of Risks and Opportunities",
    'description': """
        Extends matrix.block.line (Risks and Opportunities) with a conditional profile,
        active when the Identifier is "Information security" and the record is a risk:
        affected asset, threat and threat agent, a workflow of initial assessment ->
        treatment/controls -> residual assessment -> risk acceptance, and the
        "Information Security Risk Assessment" indicator (Impact x Probability,
        scale 1-25).
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
