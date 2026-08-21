# -*- coding: utf-8 -*-
{
    'name': "Inventario de Activos de Información - Campos ISO 27001",
    'summary': "Campos adicionales y reporte Excel para el Inventario de Activos de Información",
    'description': """
        Extiende el Inventario de Activos de Información (cyber_matrix.block.line) con
        los campos de propietario, custodio, titularidad, clasificación de la información,
        estado y fechas de revisión, y agrega un reporte Excel con el detalle consolidado.
    """,
    'author': "Soy Calidad",
    'category': 'iso27001',
    'version': '18.0.1.0.0',
    'depends': [
        'soy_cybersecurity_cybersecurity',
        'hr',
        'report_xlsx',
    ],
    'data': [
        'views/cyber_matrix_block_line.xml',
        'report/asset_inventory_report.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
