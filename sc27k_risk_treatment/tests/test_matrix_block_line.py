# -*- coding: utf-8 -*-
from lxml import etree

from .common import TestRiskTreatmentBase

_SIX_CRITERIA_NAMES = {
    'Probabilidad', 'Confidencialidad', 'Integridad', 'Disponibilidad', 'Trazabilidad', 'Autenticidad',
}


class TestMatrixBlockLine(TestRiskTreatmentBase):

    def test_new_fields_defaults(self):
        self.assertEqual(self.risk.sc27k_asset_id, self.asset)
        self.assertEqual(self.risk.sc27k_threat, 'Ransomware / phishing / robo de credenciales')
        self.assertEqual(self.risk.sc27k_threat_agent, 'Ciberdelincuente / usuario interno')
        self.assertEqual(self.risk.sc27k_treatment_state, 'pending')
        self.assertEqual(self.risk.sc27k_treatment_approval_state, 'pending')
        self.assertEqual(self.risk.sc27k_residual_acceptance_state, 'pending')

    def test_is_security_profile_true_for_risk_with_matching_identifier(self):
        self.assertTrue(self.risk.sc27k_is_security_profile)

    def test_is_security_profile_false_for_other_identifier(self):
        self.assertFalse(self.risk_other_identifier.sc27k_is_security_profile)

    def test_is_security_profile_false_for_opportunity(self):
        self.assertFalse(self.opportunity_security_identifier.sc27k_is_security_profile)

    def test_initial_ntr_is_probability_times_max_impact(self):
        # Impacto = max(4, 2, 3, 1, 1) = 4; Valor de riesgo = Probabilidad(3) x 4 = 12.
        self._set_results(self.risk, 'result_ids', {
            'probability': 3,
            'confidentiality': 4,
            'integrity': 2,
            'availability': 3,
            'traceability': 1,
            'authenticity': 1,
        })
        self.assertEqual(self.risk.sc27k_initial_ntr, 12)
        self.assertEqual(self.risk.sc27k_risk_level, 'high')

    def test_initial_ntr_ignores_non_impact_criteria_for_the_max(self):
        # Only Probabilidad and the 5 impact dimensions feed the formula; the highest
        # single value here is Probabilidad(5) itself, which must NOT count as impact.
        self._set_results(self.risk, 'result_ids', {
            'probability': 5,
            'confidentiality': 2,
            'integrity': 1,
            'availability': 1,
            'traceability': 1,
            'authenticity': 1,
        })
        self.assertEqual(self.risk.sc27k_initial_ntr, 10)  # 5 x max(2,1,1,1,1)

    def test_risk_level_bands(self):
        cases = (
            ({'probability': 1, 'confidentiality': 2}, 'low'),        # 1 x 2 = 2
            ({'probability': 2, 'confidentiality': 4}, 'medium'),     # 2 x 4 = 8
            ({'probability': 3, 'confidentiality': 4}, 'high'),       # 3 x 4 = 12
            ({'probability': 5, 'confidentiality': 5}, 'critical'),   # 5 x 5 = 25
        )
        for values, expected_level in cases:
            risk = self.line_obj.create({
                'name': f'Riesgo de prueba {expected_level}',
                'type': 'risk',
                'system_id': self.security_system.id,
            })
            self._set_results(risk, 'result_ids', values)
            self.assertEqual(risk.sc27k_risk_level, expected_level, values)

    def test_risk_level_not_set_outside_security_profile(self):
        self._set_results(self.risk_other_identifier, 'result_ids', {
            'probability': 5, 'confidentiality': 5,
        })
        self.assertFalse(self.risk_other_identifier.sc27k_risk_level)

    def test_residual_ntr_and_level(self):
        self._set_results(self.risk, 'sc27k_residual_result_ids', {
            'probability': 3, 'integrity': 4, 'availability': 2,
        })
        self.assertEqual(self.risk.sc27k_residual_ntr, 12)
        self.assertEqual(self.risk.sc27k_residual_risk_level, 'high')

    def test_residual_ntr_recomputes_when_results_change(self):
        self._set_results(self.risk, 'sc27k_residual_result_ids', {
            'probability': 1, 'confidentiality': 1,
        })
        self.assertEqual(self.risk.sc27k_residual_ntr, 1)
        self.assertEqual(self.risk.sc27k_residual_risk_level, 'low')

        self.risk.sc27k_residual_result_ids.unlink()
        self._set_results(self.risk, 'sc27k_residual_result_ids', {
            'probability': 5, 'confidentiality': 5,
        })
        self.assertEqual(self.risk.sc27k_residual_ntr, 25)
        self.assertEqual(self.risk.sc27k_residual_risk_level, 'critical')

    def test_treatment_approval_workflow(self):
        self.risk.sc27k_action_approve_treatment()
        self.assertEqual(self.risk.sc27k_treatment_approval_state, 'approved')
        self.assertEqual(self.risk.sc27k_treatment_approved_by_id, self.env.user)
        self.assertTrue(self.risk.sc27k_treatment_approval_date)

        self.risk.sc27k_action_request_treatment_rework()
        self.assertEqual(self.risk.sc27k_treatment_approval_state, 'rework')

    def test_residual_acceptance_workflow(self):
        self.risk.sc27k_action_accept_residual_risk()
        self.assertEqual(self.risk.sc27k_residual_acceptance_state, 'accepted')
        self.assertEqual(self.risk.sc27k_residual_decision, 'accept')
        self.assertEqual(self.risk.sc27k_residual_accepted_by_id, self.env.user)
        self.assertTrue(self.risk.sc27k_residual_acceptance_date)

        self.risk.sc27k_action_request_additional_treatment()
        self.assertEqual(self.risk.sc27k_residual_acceptance_state, 'additional_treatment')
        self.assertEqual(self.risk.sc27k_residual_decision, 'additional_treatment')

    def test_residual_evaluation_onchange_seeds_result_lines(self):
        self.risk.sc27k_residual_evaluation_id = self.security_evaluation.id
        self.risk._sc27k_onchange_residual_evaluation_id()
        self.assertEqual(len(self.risk.sc27k_residual_result_ids), 6)
        self.assertEqual(
            set(self.risk.sc27k_residual_result_ids.mapped('criterio_id.name')),
            _SIX_CRITERIA_NAMES,
        )

    def test_residual_evaluation_onchange_replaces_previous_lines(self):
        self.risk.sc27k_residual_evaluation_id = self.security_evaluation.id
        self.risk._sc27k_onchange_residual_evaluation_id()
        first_line_ids = self.risk.sc27k_residual_result_ids.ids

        self.risk._sc27k_onchange_residual_evaluation_id()
        self.assertEqual(len(self.risk.sc27k_residual_result_ids), 6)
        self.assertFalse(set(first_line_ids) & set(self.risk.sc27k_residual_result_ids.ids))

    def test_acciones_and_origenes_tabs_hidden_for_security_profile(self):
        # Querying the already-fetched arch by @string is fine here: the "no @string
        # selector" rule only applies to <xpath> elements Odoo evaluates while
        # composing inherited views, not to plain lxml queries over the result.
        arch = etree.fromstring(self.line_obj.get_view(view_type='form')['arch'])

        origin_pages = arch.xpath("//page[@name='origin_ids']")
        self.assertEqual(len(origin_pages), 1)
        self.assertEqual(origin_pages[0].get('invisible'), 'sc27k_is_security_profile')

        acciones_pages = arch.xpath("//page[@string='Acciones']")
        self.assertEqual(len(acciones_pages), 1)
        self.assertEqual(acciones_pages[0].get('invisible'), 'sc27k_is_security_profile')

        treatment_pages = arch.xpath("//page[@string='Tratamiento / Controles']")
        self.assertEqual(len(treatment_pages), 1)
        self.assertNotEqual(treatment_pages[0].get('invisible'), 'sc27k_is_security_profile')

    def test_mgmtsystem_action_implementation_record_field(self):
        action = self.env['mgmtsystem.action'].create({
            'name': 'Implementar MFA en accesos remotos',
            'type_action_id': self.env['mgmtsystem.action.type'].create({'name': 'Preventiva'}).id,
            'sc27k_implementation_record': 'Evidencia: captura de configuración MFA en Azure AD',
        })
        self.assertEqual(
            action.sc27k_implementation_record,
            'Evidencia: captura de configuración MFA en Azure AD',
        )
