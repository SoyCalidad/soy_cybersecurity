# -*- coding: utf-8 -*-
{
    'name': "Information Asset Inventory - ISO 27001 Fields",
    'summary': "Additional fields and Excel report for the Information Asset Inventory",
    'description': """
        Extends the Information Asset Inventory (cyber_matrix.block.line) with the owner,
        custodian, ownership, information classification, status and review date fields,
        and adds an Excel report with the consolidated detail.
    """,
    'author': "Soy Calidad",
    'category': 'iso27001',
    'version': '18.0.1.0.0',
    'depends': [
        'sc27k_base',
        'soy_cybersecurity_cybersecurity',
        'hr',
        'report_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        
        'data/mgmtsystem_context_system.xml',
        'views/cyber_matrix_block_line.xml',
        'report/asset_inventory_report.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
