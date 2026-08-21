# -*- coding: utf-8 -*-
import io
import zipfile

from .common import TestRiskTreatmentBase

_REPORT_NAME = 'sc27k_risk_treatment.report_risk_xlsx'


class TestRiskReport(TestRiskTreatmentBase):

    def _shared_strings(self, xlsx_bytes):
        with zipfile.ZipFile(io.BytesIO(xlsx_bytes)) as archive:
            return archive.read('xl/sharedStrings.xml').decode('utf-8')

    def test_report_action_is_bound_to_the_model(self):
        report_action = self.env.ref('sc27k_risk_treatment.sc27k_risk_treatment_report_xlsx')
        self.assertEqual(report_action.report_type, 'xlsx')
        self.assertEqual(report_action.model, 'matrix.block.line')
        self.assertEqual(report_action.binding_type, 'report')

    def test_report_generation(self):
        self._set_results(self.risk, 'result_ids', {
            'probability': 3, 'confidentiality': 4, 'integrity': 2,
        })
        self._set_results(self.risk, 'sc27k_residual_result_ids', {
            'probability': 1, 'confidentiality': 2,
        })

        xlsx_bytes, report_format = self.env['ir.actions.report']._render_xlsx(
            _REPORT_NAME, self.risk.ids, {}
        )
        self.assertEqual(report_format, 'xlsx')
        self.assertTrue(xlsx_bytes)

        strings = self._shared_strings(xlsx_bytes)
        self.assertIn('MATRIZ DE RIESGOS DE SEGURIDAD DE LA INFORMACIÓN', strings)
        self.assertIn('Nivel de riesgo inicial', strings)
        self.assertIn('Nivel de riesgo residual', strings)
        self.assertIn(self.risk.name, strings)
        self.assertIn(self.risk.sc27k_threat, strings)
        self.assertIn(self.asset.name, strings)

    def test_report_generation_with_empty_evaluations(self):
        xlsx_bytes, report_format = self.env['ir.actions.report']._render_xlsx(
            _REPORT_NAME, self.risk.ids, {}
        )
        self.assertEqual(report_format, 'xlsx')
        self.assertTrue(xlsx_bytes)

    def test_report_generation_for_multiple_risks(self):
        second_risk = self.line_obj.create({
            'name': 'Fuga de información en servicio de correo',
            'type': 'risk',
            'system_id': self.security_system.id,
        })
        xlsx_bytes, report_format = self.env['ir.actions.report']._render_xlsx(
            _REPORT_NAME, (self.risk + second_risk).ids, {}
        )
        self.assertEqual(report_format, 'xlsx')
        strings = self._shared_strings(xlsx_bytes)
        self.assertIn(self.risk.name, strings)
        self.assertIn(second_risk.name, strings)
