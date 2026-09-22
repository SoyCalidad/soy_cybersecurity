# -*- coding: utf-8 -*-
import base64
import io

from odoo import _, fields, models
from odoo.exceptions import UserError

# (header, width) per column, in the exact order and wording of the "Formato reporte de
# riesgos de SI.xlsx" template. Typos in the source ("Responasble") are kept verbatim to
# match the approved format.
_COLUMNS = [
    (_('Nombre del riesgo'), 26), (_('Proceso'), 18), (_('Activo'), 22), (_('Tipo'), 16),

    (_('Descripción'), 30), (_('Agente de la causa'), 18), (_('Causa'), 26), (_('Efecto'), 26),

    (_('Responsable del riesgo'), 22),

    (_('Amenaza'), 26), (_('Agente de la amenaza'), 24),

    (_('Probabilidad'), 14), (_('Confidencialidad'), 14), (_('Integridad'), 12),

    (_('Disponibilidad'), 14), (_('Trazabilidad'), 14), (_('Autenticidad'), 14),

    (_('Impacto inicial'), 12), (_('Valor de riesgo inicial'), 14), (_('Nivel de riesgo inicial'), 16),

    (_('Tratamiento / Salvaguarda'), 20), (_('Descripción del tratamiento'), 28),

    (_('Fecha inicio'), 12), (_('Fecha objetivo'), 12), (_('Estado'), 14), (_('Controles'), 28),

    (_('Probabilidad'), 14), (_('Confidencialidad'), 14), (_('Integridad'), 12),

    (_('Disponibilidad'), 14), (_('Trazabilidad'), 14), (_('Autenticidad'), 14),

    (_('Impacto inicial'), 12), (_('Valor de riesgo residual'), 16), (_('Nivel de riesgo residual'), 16),

    (_('Decisión'), 20), (_('Responasble'), 18), (_('Comentario'), 28),
]

_GROUP_HEADERS = [
    (_('IDENTIFICACIÓN DEL RIESGO Y ACTIVO'), 0, 8),
    (_('AMENAZA'), 9, 10),
    (_('EVALUACIÓN INICIAL'), 11, 19),
    (_('TRATAMIENTO'), 20, 25),
    (_('EVALUACIÓN RIESGO RESIDUAL'), 26, 34),
    (_('RIESGO RESIDUAL'), 35, 37),
]

_IMPACT_CRITERIA_ORDER = (
    _('Confidencialidad'),
    _('Integridad'),
    _('Disponibilidad'),
    _('Trazabilidad'),
    _('Autenticidad'),
)
_INITIAL_LEVEL_COLUMN = 18
_RESIDUAL_LEVEL_COLUMN = 33
_LEFT_ALIGN_COLUMNS = (0, 4, 6, 7, 21)


class RiskReportXlsx(models.AbstractModel):
    """xlsx layout for the "Formato reporte de riesgos de SI" template. Also used, via
    ``self.env[...]`` delegation, by RiskMatrixReportXlsx below — both reports share
    the exact same sheet, just over a different set of matrix.block.line records.
    """
    _name = 'report.sc27k_risk_treatment.report_risk_xlsx'
    _description = 'Reporte Excel de Riesgos de Seguridad de la Información'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        formats = self._sc27k_build_formats(workbook)
        self._sc27k_write_risk_sheet(workbook, formats, 'Matriz de Riesgos SI', lines)

    def _sc27k_build_formats(self, workbook):
        return {
            'title': workbook.add_format({
                'font_size': 22, 'bold': True, 'align': 'center', 'valign': 'vcenter',
            }),
            'info': workbook.add_format({
                'font_size': 10, 'bold': True, 'align': 'left', 'valign': 'vcenter',
            }),
            'group': workbook.add_format({
                'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter',
                'bg_color': '#1F3864', 'font_color': 'white', 'border': 1,
            }),
            'header': workbook.add_format({
                'font_size': 10, 'bold': True, 'align': 'center', 'valign': 'vcenter',
                'bg_color': '#D9E1F2', 'text_wrap': True, 'border': 1,
            }),
            'left': workbook.add_format({
                'font_size': 10, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True, 'border': 1,
            }),
            'center': workbook.add_format({
                'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 1,
            }),
            'critical': workbook.add_format({
                'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                'border': 1, 'bg_color': '#F8CBAD',
            }),
        }

    def _sc27k_write_risk_sheet(self, workbook, formats, sheet_name, lines):
        sheet = workbook.add_worksheet(sheet_name)
        last_col = len(_COLUMNS) - 1

        for col, (_header, width) in enumerate(_COLUMNS):
            sheet.set_column(col, col, width)

        company = self.env.company
        if company.logo:
            buf_image = io.BytesIO(base64.b64decode(company.logo))
            sheet.insert_image('A1', 'logo.png', {'image_data': buf_image, 'x_scale': 0.3, 'y_scale': 0.3})
        sheet.merge_range(0, 0, 2, last_col, _('Information Security Risk Matrix'), formats['title'])
        sheet.set_row(0, 22)
        sheet.set_row(1, 22)
        sheet.set_row(2, 22)
        report_date = fields.Date.to_string(fields.Date.context_today(self))
        sheet.write(3, 0, f'Fecha: {report_date}', formats['info'])

        row = 5
        for label, start_col, end_col in _GROUP_HEADERS:
            sheet.merge_range(row, start_col, row, end_col, label, formats['group'])
        row += 1
        for col, (header, _width) in enumerate(_COLUMNS):
            sheet.write(row, col, header, formats['header'])
        sheet.freeze_panes(row + 1, 0)

        row += 1
        for line in lines:
            self._sc27k_write_risk_row(sheet, formats, row, line)
            row += 1

    def _sc27k_write_risk_row(self, sheet, formats, row, line):
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
            if col == _INITIAL_LEVEL_COLUMN and line.sc27k_risk_level in ('high', 'critical'):
                fmt = formats['critical']
            elif col == _RESIDUAL_LEVEL_COLUMN and line.sc27k_residual_risk_level in ('high', 'critical'):
                fmt = formats['critical']
            elif col in _LEFT_ALIGN_COLUMNS:
                fmt = formats['left']
            else:
                fmt = formats['center']
            sheet.write(row, col, value, fmt)

    def _sc27k_criteria_values(self, results):
        """Map each evaluation.result in ``results`` to its value, keyed by
        criterio name (Probabilidad / Confidencialidad / Integridad / Disponibilidad /
        Trazabilidad / Autenticidad).
        """
        return {result.criterio_id.name: result.value for result in results if result.criterio_id}

    def _sc27k_max_impact(self, criteria_values):
        impact_values = [criteria_values[name] for name in _IMPACT_CRITERIA_ORDER if name in criteria_values]
        return max(impact_values) if impact_values else ''


class RiskMatrixReportXlsx(models.AbstractModel):
    _name = 'report.sc27k_risk_treatment.report_risk_matrix_xlsx'
    _description = 'Reporte Excel de Matriz de Riesgos de Seguridad de la Información'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, matrices):
        risk_report = self.env['report.sc27k_risk_treatment.report_risk_xlsx']
        formats = risk_report._sc27k_build_formats(workbook)
        for matrix in matrices:
            lines = matrix.line_ids.filtered('sc27k_is_security_profile')
            if not lines:
                raise UserError(_(
                    'La matriz "%(matrix_name)s" no tiene riesgos con el Identificador '
                    '"Seguridad de la información"; no hay nada que reportar.',
                    matrix_name=matrix.name or matrix.code or matrix.id,
                ))
            risk_report._sc27k_write_risk_sheet(
                workbook, formats, matrix.name or matrix.code or 'Matriz', lines)
