# -*- coding: utf-8 -*-
from psycopg2 import IntegrityError

from odoo.tools import mute_logger

from .common import TestAssetInventoryBase


class TestCyberMatrixBlockLine(TestAssetInventoryBase):

    def test_new_fields_defaults(self):
        self.assertEqual(self.asset.sc27k_asset_code, 'ACT-HW-TEST-001')
        self.assertEqual(self.asset.sc27k_owner_job_id, self.job_cto)
        self.assertEqual(self.asset.sc27k_custodian_id, self.employee)
        self.assertEqual(self.asset.sc27k_asset_state, 'active')

    def test_criticality_low(self):
        self._set_evaluation_results(self.asset, self.low_alternatives, 2)
        self.assertEqual(self.asset.ntr, 8)
        self.assertEqual(self.asset.sc27k_criticality, 'low')

    def test_criticality_medium(self):
        self._set_evaluation_results(self.asset, self.medium_alternatives, 4)
        self.assertEqual(self.asset.ntr, 64)
        self.assertEqual(self.asset.sc27k_criticality, 'medium')

    def test_criticality_high(self):
        self._set_evaluation_results(self.asset, self.high_alternatives, 8)
        self.assertEqual(self.asset.ntr, 512)
        self.assertEqual(self.asset.sc27k_criticality, 'high')

    def test_criticality_recomputes_on_result_change(self):
        self._set_evaluation_results(self.asset, self.low_alternatives, 2)
        self.assertEqual(self.asset.sc27k_criticality, 'low')
        self._set_evaluation_results(self.asset, self.high_alternatives, 8)
        self.assertEqual(self.asset.sc27k_criticality, 'high')

    def test_asset_code_unique_per_company(self):
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            with self.cr.savepoint():
                self.line_obj.create({
                    'name': 'Segundo laptop',
                    'sc27k_asset_code': self.asset.sc27k_asset_code,
                })

    def test_asset_code_reusable_across_companies(self):
        other_company = self.env['res.company'].create({'name': 'Otra Compañía'})
        other_company_asset = self.line_obj.create({
            'name': 'Laptop de otra compañía',
            'sc27k_asset_code': self.asset.sc27k_asset_code,
            'company_id': other_company.id,
        })
        self.assertEqual(other_company_asset.sc27k_asset_code, self.asset.sc27k_asset_code)
