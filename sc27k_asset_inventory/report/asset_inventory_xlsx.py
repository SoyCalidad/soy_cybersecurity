# -*- coding: utf-8 -*-
from odoo import models

_HEADERS = [
    'Código', 'Nombre del activo', 'Tipo de activo', 'Descripción', 'Proceso',
    'Propietario del activo', 'Usuario asignado / Custodio', 'Ubicación', 'Titularidad',
    'Clasificación de la información', 'Datos personales', 'Confidencialidad', 'Integridad',
    'Disponibilidad', 'Criticidad', 'Estado', 'Última revisión', 'Próxima revisión',
]
_COLUMN_WIDTHS = [14, 30, 16, 35, 20, 22, 24, 16, 16, 22, 16, 16, 12, 14, 12, 12, 14, 14]
# Left-aligned text columns; the rest are centered.
_LEFT_ALIGN_COLUMNS = {1, 3}
_CRITICALITY_COLUMN = 14


class AssetInventoryXlsx(models.AbstractModel):
    _name = 'report.sc27k_asset_inventory.report_asset_inventory_xlsx'
    _description = 'Reporte Excel de Inventario de Activos de Información'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        header_format = workbook.add_format({
            'font_size': 10, 'bg_color': '#1F3864', 'font_color': 'white',
            'align': 'center', 'valign': 'vcenter', 'bold': True, 'text_wrap': True, 'border': 1,
        })
        left_format = workbook.add_format({
            'font_size': 10, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True, 'border': 1,
        })
        center_format = workbook.add_format({
            'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 1,
        })
        critical_format = workbook.add_format({
            'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 1,
            'bg_color': '#F8CBAD',
        })

        sheet = workbook.add_worksheet('Inventario de Activos')
        for col, width in enumerate(_COLUMN_WIDTHS):
            sheet.set_column(col, col, width)
        for col, header in enumerate(_HEADERS):
            sheet.write(0, col, header, header_format)
        sheet.freeze_panes(1, 0)

        ownership_labels = dict(lines._fields['sc27k_ownership'].selection)
        classification_labels = dict(lines._fields['sc27k_information_classification'].selection)
        personal_data_labels = dict(lines._fields['sc27k_personal_data_level'].selection)
        state_labels = dict(lines._fields['sc27k_asset_state'].selection)
        criticality_labels = dict(lines._fields['sc27k_criticality'].selection)

        row = 1
        for line in lines:
            criteria_values = {
                result.criterio_id.name: result.alternative.name
                for result in line.result_ids if result.criterio_id
            }
            values = [
                line.sc27k_asset_code or '',
                line.name or '',
                ', '.join(line.asset_type_id.mapped('name')),
                line.description or '',
                line.process_id.name or '',
                line.sc27k_owner_job_id.name or '',
                line.sc27k_custodian_id.name or '',
                ', '.join(line.location_id.mapped('name')),
                ownership_labels.get(line.sc27k_ownership, ''),
                classification_labels.get(line.sc27k_information_classification, ''),
                personal_data_labels.get(line.sc27k_personal_data_level, ''),
                criteria_values.get('Confidencialidad', ''),
                criteria_values.get('Integridad', ''),
                criteria_values.get('Disponibilidad', ''),
                criticality_labels.get(line.sc27k_criticality, ''),
                state_labels.get(line.sc27k_asset_state, ''),
                str(line.sc27k_last_review_date or ''),
                str(line.sc27k_next_review_date or ''),
            ]
            is_high_criticality = line.sc27k_criticality == 'high'
            for col, value in enumerate(values):
                if col == _CRITICALITY_COLUMN and is_high_criticality:
                    fmt = critical_format
                elif col in _LEFT_ALIGN_COLUMNS:
                    fmt = left_format
                else:
                    fmt = center_format
                sheet.write(row, col, value, fmt)
            row += 1
