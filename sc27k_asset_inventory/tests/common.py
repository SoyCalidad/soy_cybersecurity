# -*- coding: utf-8 -*-
from odoo.addons.base.tests.common import BaseCommon
from odoo.tests.common import tagged


@tagged('post_install', '-at_install')
class TestAssetInventoryBase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.line_obj = cls.env['cyber_matrix.block.line']
        cls.result_obj = cls.env['cyber_evaluation.result']
        cls.evaluation = cls.env.ref('soy_cybersecurity_cybersecurity.cyber_evaluation_1')

        # Confidencialidad, Integridad and Disponibilidad each have a "low"
        # (1-3), "medium" (4-7), and "high" (8-10) alternative; a fixed value
        # per band from each criterio gives a deterministic product (ntr).
        cls.low_alternatives = cls.env['cyber_evaluation.criterio.line'].browse([
            cls.env.ref('soy_cybersecurity_cybersecurity.criterio_line_1_2').id,
            cls.env.ref('soy_cybersecurity_cybersecurity.criterio_line_2_1').id,
            cls.env.ref('soy_cybersecurity_cybersecurity.criterio_line_3_1').id,
        ])
        cls.medium_alternatives = cls.env['cyber_evaluation.criterio.line'].browse([
            cls.env.ref('soy_cybersecurity_cybersecurity.criterio_line_1_3').id,
            cls.env.ref('soy_cybersecurity_cybersecurity.criterio_line_2_2').id,
            cls.env.ref('soy_cybersecurity_cybersecurity.criterio_line_3_2').id,
        ])
        cls.high_alternatives = cls.env['cyber_evaluation.criterio.line'].browse([
            cls.env.ref('soy_cybersecurity_cybersecurity.criterio_line_1_4').id,
            cls.env.ref('soy_cybersecurity_cybersecurity.criterio_line_2_3').id,
            cls.env.ref('soy_cybersecurity_cybersecurity.criterio_line_3_3').id,
        ])

        cls.job_cto = cls.env['hr.job'].create({'name': 'CTO'})
        cls.employee = cls.env['hr.employee'].create({'name': 'Juan Perez'})

        cls.security_system = cls.env.ref('sc27k_base.system_cybersecurity')
        cls.other_system = cls.env.ref('hola_calidad.policy_system_1')

        cls.asset = cls.line_obj.create({
            'name': 'Laptop corporativa de desarrollo',
            'sc27k_asset_code': 'ACT-HW-TEST-001',
            'sc27k_owner_job_id': cls.job_cto.id,
            'sc27k_custodian_id': cls.employee.id,
            'sc27k_ownership': 'corporate',
            'sc27k_information_classification': 'not_applicable',
            'sc27k_personal_data_level': 'may_process',
            'sc27k_last_review_date': '2026-08-12',
            'sc27k_next_review_date': '2027-08-12',
            'evaluation_id': cls.evaluation.id,
        })
        cls.security_asset = cls.line_obj.create({
            'name': 'Servidor de aplicaciones',
            'sc27k_asset_code': 'ACT-SEC-TEST-001',
            'system_id': cls.security_system.id,
            'sc27k_asset_type': 'SW',
        })

    def _set_evaluation_results(self, line, alternatives, value):
        """Replace the evaluation results of ``line`` with one result per
        ``alternatives`` line, each carrying ``value``. Recomputes ``ntr``
        and, transitively, ``sc27k_criticality``.
        """
        results = self.result_obj.create([{
            'criterio_id': alternative.criterio_id.id,
            'alternative': alternative.id,
            'value': value,
        } for alternative in alternatives])
        line.result_ids = [(6, 0, results.ids)]
