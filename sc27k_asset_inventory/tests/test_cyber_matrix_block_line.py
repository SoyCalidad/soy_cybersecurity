# -*- coding: utf-8 -*-
from lxml import etree
from psycopg2 import IntegrityError

from odoo.tools import mute_logger

from .common import TestAssetInventoryBase

_MAGERIT_CODES = {'D', 'K', 'S', 'SW', 'HW', 'COM', 'MEDIA', 'AUX', 'L', 'P'}
_SECURITY_PROFILE_HIDDEN_FIELDS = (
    'department_id', 'resource_id', 'asset_susceptible_to_fraud',
    'asset_vital_for_organization', 'language_id', 'storage_medium', 'asset_type_id',
)


class TestCyberMatrixBlockLine(TestAssetInventoryBase):

    def test_new_fields_defaults(self):
        self.assertEqual(self.asset.sc27k_asset_code, 'ACT-HW-TEST-001')
        self.assertEqual(self.asset.sc27k_owner_job_id, self.job_cto)
        self.assertEqual(self.asset.sc27k_custodian_id, self.employee)
        self.assertEqual(self.asset.sc27k_asset_state, 'active')

    def test_is_security_profile_true_for_matching_identifier(self):
        self.assertTrue(self.security_asset.sc27k_is_security_profile)

    def test_is_security_profile_false_for_other_identifier(self):
        self.assertFalse(self.asset.sc27k_is_security_profile)

    def test_asset_type_selection_has_the_ten_magerit_codes(self):
        selection_codes = {key for key, _label in self.asset._fields['sc27k_asset_type'].selection}
        self.assertEqual(selection_codes, _MAGERIT_CODES)
        self.assertEqual(self.security_asset.sc27k_asset_type, 'SW')

    def test_legacy_fields_hidden_for_security_profile(self):
        arch = etree.fromstring(self.line_obj.get_view(view_type='form')['arch'])
        for field_name in _SECURITY_PROFILE_HIDDEN_FIELDS:
            matches = arch.xpath(f"//field[@name='{field_name}']")
            self.assertTrue(matches, field_name)
            self.assertEqual(
                matches[0].get('invisible'), 'sc27k_is_security_profile', field_name)

        asset_type_matches = arch.xpath("//field[@name='sc27k_asset_type']")
        self.assertTrue(asset_type_matches)
        self.assertEqual(asset_type_matches[0].get('invisible'), 'not sc27k_is_security_profile')

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
