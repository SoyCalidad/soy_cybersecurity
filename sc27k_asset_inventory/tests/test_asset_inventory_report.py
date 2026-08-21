# -*- coding: utf-8 -*-
import io
import zipfile

from .common import TestAssetInventoryBase

_REPORT_NAME = 'sc27k_asset_inventory.report_asset_inventory_xlsx'


class TestAssetInventoryReport(TestAssetInventoryBase):

    def _shared_strings(self, xlsx_bytes):
        with zipfile.ZipFile(io.BytesIO(xlsx_bytes)) as archive:
            return archive.read('xl/sharedStrings.xml').decode('utf-8')

    def test_report_action_is_bound_to_the_model(self):
        report_action = self.env.ref('sc27k_asset_inventory.sc27k_asset_inventory_report_xlsx')
        self.assertEqual(report_action.report_type, 'xlsx')
        self.assertEqual(report_action.model, 'cyber_matrix.block.line')
        self.assertEqual(report_action.binding_type, 'report')

    def test_report_generation(self):
        xlsx_bytes, report_format = self.env['ir.actions.report']._render_xlsx(
            _REPORT_NAME, self.asset.ids, {}
        )
        self.assertEqual(report_format, 'xlsx')
        self.assertTrue(xlsx_bytes)

        strings = self._shared_strings(xlsx_bytes)
        self.assertIn('Código', strings)
        self.assertIn('Criticidad', strings)
        self.assertIn(self.asset.sc27k_asset_code, strings)
        self.assertIn(self.asset.name, strings)
        self.assertIn(self.job_cto.name, strings)
        self.assertIn(self.employee.name, strings)

    def test_report_includes_evaluation_criteria(self):
        self._set_evaluation_results(self.asset, self.high_alternatives, 8)
        xlsx_bytes, _fmt = self.env['ir.actions.report']._render_xlsx(
            _REPORT_NAME, self.asset.ids, {}
        )
        strings = self._shared_strings(xlsx_bytes)
        self.assertIn('Alta', strings)

    def test_report_generation_with_empty_optional_fields(self):
        bare_asset = self.line_obj.create({
            'name': 'Activo sin datos opcionales',
            'sc27k_asset_code': 'ACT-BARE-001',
        })
        xlsx_bytes, report_format = self.env['ir.actions.report']._render_xlsx(
            _REPORT_NAME, bare_asset.ids, {}
        )
        self.assertEqual(report_format, 'xlsx')
        self.assertTrue(xlsx_bytes)
