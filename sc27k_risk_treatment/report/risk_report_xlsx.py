# -*- coding: utf-8 -*-
import base64
import io

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import LazyTranslate

from ..models.evaluation_criterio import SC27K_IMPACT_CRITERION_TYPES

_lt = LazyTranslate(__name__)

# (header, width) per column, in the exact order of the information security risk report
# template. The headers are lazily translated: they are translated when written.
_COLUMNS = [
    (_lt('Risk name'), 26), (_lt('Process'), 18), (_lt('Asset'), 22), (_lt('Type'), 16),

    (_lt('Description'), 30), (_lt('Agent of the cause'), 18), (_lt('Cause'), 26), (_lt('Effect'), 26),

    (_lt('Risk responsible'), 22),

    (_lt('Threat'), 26), (_lt('Agent of the threat'), 24),

    (_lt('Probability'), 14), (_lt('Confidentiality'), 14), (_lt('Integrity'), 12),

    (_lt('Availability'), 14), (_lt('Traceability'), 14), (_lt('Authenticity'), 14),

    (_lt('Initial impact'), 12), (_lt('Initial risk value'), 14), (_lt('Initial risk level'), 16),

    (_lt('Treatment / Safeguard'), 20), (_lt('Treatment description'), 28),

    (_lt('Start date'), 12), (_lt('Target date'), 12), (_lt('Status'), 14), (_lt('Controls'), 28),

    (_lt('Probability'), 14), (_lt('Confidentiality'), 14), (_lt('Integrity'), 12),

    (_lt('Availability'), 14), (_lt('Traceability'), 14), (_lt('Authenticity'), 14),

    (_lt('Residual impact'), 12), (_lt('Residual risk value'), 16), (_lt('Residual risk level'), 16),

    (_lt('Decision'), 20), (_lt('Person responsible'), 18), (_lt('Comment'), 28),
]

_GROUP_HEADERS = [
    (_lt('RISK AND ASSET IDENTIFICATION'), 0, 8),
    (_lt('THREAT'), 9, 10),
    (_lt('INITIAL ASSESSMENT'), 11, 19),
    (_lt('TREATMENT'), 20, 25),
    (_lt('RESIDUAL RISK ASSESSMENT'), 26, 34),
    (_lt('RESIDUAL RISK'), 35, 37),
]

_INITIAL_LEVEL_COLUMN = 18
_RESIDUAL_LEVEL_COLUMN = 33
_LEFT_ALIGN_COLUMNS = (0, 4, 6, 7, 21)


class RiskReportXlsx(models.AbstractModel):
    """xlsx layout for the information security risk report template. Also used, via
    ``self.env[...]`` delegation, by RiskMatrixReportXlsx below — both reports share
    the exact same sheet, just over a different set of matrix.block.line records.
    """
    _name = 'report.sc27k_risk_treatment.report_risk_xlsx'
    _description = 'Information Security Risk Excel Report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        formats = self._sc27k_build_formats(workbook)
        self._sc27k_write_risk_sheet(workbook, formats, _('IS Risk Matrix'), lines)

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
        sheet.write(3, 0, _('Date: %s', report_date), formats['info'])

        row = 5
        for label, start_col, end_col in _GROUP_HEADERS:
            sheet.merge_range(row, start_col, row, end_col, self.env._(label), formats['group'])
        row += 1
        for col, (header, _width) in enumerate(_COLUMNS):
            sheet.write(row, col, self.env._(header), formats['header'])
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
            initial_values.get('probability', ''),
            initial_values.get('confidentiality', ''),
            initial_values.get('integrity', ''),
            initial_values.get('availability', ''),
            initial_values.get('traceability', ''),
            initial_values.get('authenticity', ''),
            self._sc27k_max_impact(initial_values),
            line.sc27k_initial_ntr,
            dict(line._fields['sc27k_risk_level'].selection).get(line.sc27k_risk_level, ''),
            dict(line._fields['sc27k_treatment_option'].selection).get(line.sc27k_treatment_option, ''),
            line.sc27k_treatment_description or '',
            str(line.sc27k_treatment_start_date or ''),
            str(line.sc27k_treatment_target_date or ''),
            dict(line._fields['sc27k_treatment_state'].selection).get(line.sc27k_treatment_state, ''),
            ', '.join(line.action_ids.mapped('name')),
            residual_values.get('probability', ''),
            residual_values.get('confidentiality', ''),
            residual_values.get('integrity', ''),
            residual_values.get('availability', ''),
            residual_values.get('traceability', ''),
            residual_values.get('authenticity', ''),
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
        """Map each evaluation.result in ``results`` to its value, keyed by the
        criterion's sc27k_criterion_type (probability / confidentiality / integrity /
        availability / traceability / authenticity).
        """
        return {
            result.sc27k_criterion_type: result.value
            for result in results if result.sc27k_criterion_type
        }

    def _sc27k_max_impact(self, criteria_values):
        impact_values = [criteria_values[key] for key in SC27K_IMPACT_CRITERION_TYPES if key in criteria_values]
        return max(impact_values) if impact_values else ''


class RiskMatrixReportXlsx(models.AbstractModel):
    _name = 'report.sc27k_risk_treatment.report_risk_matrix_xlsx'
    _description = 'Information Security Risk Matrix Excel Report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, matrices):
        risk_report = self.env['report.sc27k_risk_treatment.report_risk_xlsx']
        formats = risk_report._sc27k_build_formats(workbook)
        for matrix in matrices:
            lines = matrix.line_ids.filtered('sc27k_is_security_profile')
            if not lines:
                raise UserError(_(
                    'The matrix "%(matrix_name)s" has no risks with the Identifier '
                    '"Information security"; there is nothing to report.',
                    matrix_name=matrix.name or matrix.code or matrix.id,
                ))
            risk_report._sc27k_write_risk_sheet(
                workbook, formats, matrix.name or matrix.code or _('Matrix'), lines)
