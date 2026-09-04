# -*- coding: utf-8 -*-
from odoo.addons.base.tests.common import BaseCommon
from odoo.tests.common import tagged

_CRITERIA_KEYS = (
    'probability', 'confidentiality', 'integrity', 'availability', 'traceability', 'authenticity',
)


@tagged('post_install', '-at_install')
class TestRiskTreatmentBase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.line_obj = cls.env['matrix.block.line']
        cls.asset_obj = cls.env['cyber_matrix.block.line']
        cls.result_obj = cls.env['evaluation.result']

        cls.security_system = cls.env.ref(
            'sc27k_base.system_cybersecurity')
        cls.other_system = cls.env.ref('hola_calidad.policy_system_1')
        cls.security_evaluation = cls.env.ref(
            'sc27k_risk_treatment.evaluation_security_information')

        cls.criteria = {
            key: cls.env.ref(f'sc27k_risk_treatment.criterio_security_{key}')
            for key in _CRITERIA_KEYS
        }
        cls.alternatives = {
            (key, n): cls.env.ref(f'sc27k_risk_treatment.criterio_line_security_{key}_{n}')
            for key in _CRITERIA_KEYS
            for n in range(1, 6)
        }

        cls.asset = cls.asset_obj.create({'name': 'Servidor de aplicaciones'})

        cls.risk = cls.line_obj.create({
            'name': 'Acceso no autorizado a servidor de aplicaciones',
            'type': 'risk',
            'system_id': cls.security_system.id,
            'sc27k_asset_id': cls.asset.id,
            'sc27k_threat': 'Ransomware / phishing / robo de credenciales',
            'sc27k_threat_agent': 'Ciberdelincuente / usuario interno',
        })

        cls.risk_other_identifier = cls.line_obj.create({
            'name': 'Riesgo fuera del perfil de seguridad',
            'type': 'risk',
            'system_id': cls.other_system.id,
        })

        cls.opportunity_security_identifier = cls.line_obj.create({
            'name': 'Oportunidad con identificador de seguridad',
            'type': 'opportunity',
            'system_id': cls.security_system.id,
        })

    def _set_results(self, line, field_name, values):
        """Create evaluation.result records linked to ``line`` through ``field_name``
        (``result_ids`` or ``sc27k_residual_result_ids``). ``values`` maps criteria
        keys (a subset of probability/confidentiality/integrity/availability/
        traceability/authenticity) to a 1-5 alternative value.
        """
        inverse_field = (
            'matrix_block_line_id' if field_name == 'result_ids'
            else 'sc27k_residual_matrix_block_line_id'
        )
        self.result_obj.create([
            {
                'criterio_id': self.criteria[key].id,
                'alternative': self.alternatives[(key, value)].id,
                'value': value,
                inverse_field: line.id,
            }
            for key, value in values.items()
        ])
