# -*- coding: utf-8 -*-
import base64
import io

from odoo import fields, models

# (header, width) per column, in the exact order and wording of the "Formato reporte de
# riesgos de SI.xlsx" template. Typos in the source ("Responasble") are kept verbatim to
# match the approved format.
_COLUMNS = [
    ('Nombre del riesgo', 26), ('Proceso', 18), ('Activo', 22), ('Tipo', 16),
    ('Descripción', 30), ('Agente de la causa', 18), ('Causa', 26), ('Efecto', 26),
    ('Responsable del riesgo', 22),
    ('Amenaza', 26), ('Agente de la amenaza', 24),
    ('Probabilidad', 14), ('Confidencialidad', 14), ('Integridad', 12),
    ('Disponibilidad', 14), ('Trazabilidad', 14), ('Autenticidad', 14),
    ('Impacto inicial', 12), ('Valor de riesgo inicial', 14), ('Nivel de riesgo inicial', 16),
    ('Tratamiento / Salvaguarda', 20), ('Descripción del tratamiento', 28),
    ('Fecha inicio', 12), ('Fecha objetivo', 12), ('Estado', 14), ('Controles', 28),
    ('Probabilidad', 14), ('Confidencialidad', 14), ('Integridad', 12),
    ('Disponibilidad', 14), ('Trazabilidad', 14), ('Autenticidad', 14),
    ('Impacto inicial', 12), ('Valor de riesgo residual', 16), ('Nivel de riesgo residual', 16),
    ('Decisión', 20), ('Responasble', 18), ('Comentario', 28),
]
_GROUP_HEADERS = [
    ('IDENTIFICACIÓN DEL RIESGO Y ACTIVO', 0, 8),
    ('AMENAZA', 9, 10),
    ('EVALUACIÓN INICIAL', 11, 19),
    ('TRATAMIENTO', 20, 25),
    ('EVALUACIÓN RIESGO RESIDUAL', 26, 34),
    ('RIESGO RESIDUAL', 35, 37),
]
_IMPACT_CRITERIA_ORDER = ('Confidencialidad', 'Integridad', 'Disponibilidad', 'Trazabilidad', 'Autenticidad')


class RiskReportXlsx(models.AbstractModel):
    _name = 'report.sc27k_risk_treatment.report_risk_xlsx'
    _description = 'Reporte Excel de Matriz de Riesgos de Seguridad de la Información'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        title_format = workbook.add_format({
            'font_size': 22, 'bold': True, 'align': 'center', 'valign': 'vcenter',
        })
        info_format = workbook.add_format({
            'font_size': 10, 'bold': True, 'align': 'left', 'valign': 'vcenter',
        })
        group_format = workbook.add_format({
            'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#1F3864', 'font_color': 'white', 'border': 1,
        })
        header_format = workbook.add_format({
            'font_size': 10, 'bold': True, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#D9E1F2', 'text_wrap': True, 'border': 1,
        })
        left_format = workbook.add_format({
            'font_size': 10, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True, 'border': 1,
        })
        center_format = workbook.add_format({
            'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 1,
        })
        critical_format = workbook.add_format({
            'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
            'border': 1, 'bg_color': '#F8CBAD',
        })

        sheet = workbook.add_worksheet('Matriz de Riesgos SI')
        last_col = len(_COLUMNS) - 1

        for col, (_header, width) in enumerate(_COLUMNS):
            sheet.set_column(col, col, width)

        company = self.env.company
        if company.logo:
            buf_image = io.BytesIO(base64.b64decode(company.logo))
            sheet.insert_image('A1', 'logo.png', {'image_data': buf_image, 'x_scale': 0.3, 'y_scale': 0.3})
        sheet.merge_range(0, 0, 2, last_col, 'MATRIZ DE RIESGOS DE SEGURIDAD DE LA INFORMACIÓN', title_format)
        sheet.set_row(0, 22)
        sheet.set_row(1, 22)
        sheet.set_row(2, 22)
        report_date = fields.Date.to_string(fields.Date.context_today(self))
        sheet.write(3, 0, f'Fecha: {report_date}', info_format)

        row = 5
        for label, start_col, end_col in _GROUP_HEADERS:
            sheet.merge_range(row, start_col, row, end_col, label, group_format)
        row += 1
        for col, (header, _width) in enumerate(_COLUMNS):
            sheet.write(row, col, header, header_format)
        sheet.freeze_panes(row + 1, 0)

        row += 1
        for line in lines:
            initial_values = self._sc27k_criteria_values(line.result_ids)
            residual_values = self._sc27k_criteria_values(line.sc27k_residual_result_ids)

            values = [
                line.name or '',
                line.process_id.name or '',
                line.sc27k_asset_id.name or '',
                ', '.join(line.sc27k_asset_id.asset_type_id.mapped('name')),
                line.description or '',
                line.agent_id.name or '',
                line.cause or '',
                line.effect or '',
                ', '.join(line.job_ids.mapped('name')),
                line.sc27k_threat or '',
                line.sc27k_threat_agent or '',
                initial_values.get('Probabilidad', ''),
                initial_values.get('Confidencialidad', ''),
                initial_values.get('Integridad', ''),
                initial_values.get('Disponibilidad', ''),
                initial_values.get('Trazabilidad', ''),
                initial_values.get('Autenticidad', ''),
                self._sc27k_max_impact(initial_values),
                line.sc27k_initial_ntr,
                dict(line._fields['sc27k_risk_level'].selection).get(line.sc27k_risk_level, ''),
                dict(line._fields['sc27k_treatment_option'].selection).get(line.sc27k_treatment_option, ''),
                line.sc27k_treatment_description or '',
                str(line.sc27k_treatment_start_date or ''),
                str(line.sc27k_treatment_target_date or ''),
                dict(line._fields['sc27k_treatment_state'].selection).get(line.sc27k_treatment_state, ''),
                ', '.join(line.action_ids.mapped('name')),
                residual_values.get('Probabilidad', ''),
                residual_values.get('Confidencialidad', ''),
                residual_values.get('Integridad', ''),
                residual_values.get('Disponibilidad', ''),
                residual_values.get('Trazabilidad', ''),
                residual_values.get('Autenticidad', ''),
                self._sc27k_max_impact(residual_values),
                line.sc27k_residual_ntr,
                dict(line._fields['sc27k_residual_risk_level'].selection).get(line.sc27k_residual_risk_level, ''),
                dict(line._fields['sc27k_residual_decision'].selection).get(line.sc27k_residual_decision, ''),
                line.sc27k_residual_accepted_by_id.name or '',
                line.sc27k_residual_acceptance_comment or '',
            ]

            for col, value in enumerate(values):
                if col == 18 and line.sc27k_risk_level in ('high', 'critical'):
                    fmt = critical_format
                elif col == 33 and line.sc27k_residual_risk_level in ('high', 'critical'):
                    fmt = critical_format
                elif col in (0, 4, 6, 7, 21):
                    fmt = left_format
                else:
                    fmt = center_format
                sheet.write(row, col, value, fmt)
            row += 1

    def _sc27k_criteria_values(self, results):
        """Map each evaluation.result in ``results`` to its value, keyed by
        criterio name (Probabilidad / Confidencialidad / Integridad / Disponibilidad /
        Trazabilidad / Autenticidad).
        """
        return {result.criterio_id.name: result.value for result in results if result.criterio_id}

    def _sc27k_max_impact(self, criteria_values):
        impact_values = [criteria_values[name] for name in _IMPACT_CRITERIA_ORDER if name in criteria_values]
        return max(impact_values) if impact_values else ''
