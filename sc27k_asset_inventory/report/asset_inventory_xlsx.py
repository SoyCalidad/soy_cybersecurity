# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.tools.translate import LazyTranslate

_lt = LazyTranslate(__name__)

_HEADERS = [
    _lt('Code'),
    _lt('Asset Name'),
    _lt('Asset Type'),
    _lt('Description'),
    _lt('Process'),
    _lt('Asset Owner'),
    _lt('Assigned User / Custodian'),
    _lt('Location'),
    _lt('Ownership'),
    _lt('Information Classification'),
    _lt('Personal Data'),
    _lt('Confidentiality'),
    _lt('Integrity'),
    _lt('Availability'),
    _lt('Criticality'),
    _lt('Status'),
    _lt('Last Review'),
    _lt('Next Review'),
]
_COLUMN_WIDTHS = [14, 30, 16, 35, 20, 22, 24, 16, 16, 22, 16, 16, 12, 14, 12, 12, 14, 14]
# Left-aligned text columns; the rest are centered.
_LEFT_ALIGN_COLUMNS = {1, 3}
_CRITICALITY_COLUMN = 14

# The evaluation criteria are identified by their external id, never by their (translatable)
# name.
_CRITERIA_XMLIDS = {
    'soy_cybersecurity_cybersecurity.criterio_1': 'confidentiality',
    'soy_cybersecurity_cybersecurity.criterio_2': 'integrity',
    'soy_cybersecurity_cybersecurity.criterio_3': 'availability',
}


class AssetInventoryXlsx(models.AbstractModel):
    _name = 'report.sc27k_asset_inventory.report_asset_inventory_xlsx'
    _description = 'Excel Report of Information Asset Inventory'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        header_format = workbook.add_format({
            'font_size': 10, 'bg_color': '#1F3864', 'font_color': 'white',
            'align': 'center', 'valign': 'vcenter', 'bold': True, 'text_wrap': True, 'border': 1,
        })
        left_format = workbook.add_format({
            'font_size': 10, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True, 'border': 1,
        })
        center_format = workbook.add_format({
            'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 1,
        })
        critical_format = workbook.add_format({
            'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 1,
            'bg_color': '#F8CBAD',
        })

        sheet = workbook.add_worksheet(_('Asset Inventory'))
        for col, width in enumerate(_COLUMN_WIDTHS):
            sheet.set_column(col, col, width)
        for col, header in enumerate(_HEADERS):
            sheet.write(0, col, self.env._(header), header_format)
        sheet.freeze_panes(1, 0)

        ownership_labels = dict(lines._fields['sc27k_ownership'].selection)
        classification_labels = dict(lines._fields['sc27k_information_classification'].selection)
        personal_data_labels = dict(lines._fields['sc27k_personal_data_level'].selection)
        state_labels = dict(lines._fields['sc27k_asset_state'].selection)
        criticality_labels = dict(lines._fields['sc27k_criticality'].selection)

        row = 1
        for line in lines:
            external_ids = line.result_ids.criterio_id.get_external_id()
            criteria_values = {}
            for result in line.result_ids:
                key = _CRITERIA_XMLIDS.get(external_ids.get(result.criterio_id.id))
                if key:
                    criteria_values[key] = result.alternative.name
            values = [
                line.code or '',
                line.name or '',
                ', '.join(line.asset_type_id.mapped('name')),
                line.description or '',
                line.process_id.name or '',
                line.sc27k_owner_job_id.name or '',
                line.sc27k_custodian_id.name or '',
                ', '.join(line.location_id.mapped('name')),
                ownership_labels.get(line.sc27k_ownership, ''),
                classification_labels.get(line.sc27k_information_classification, ''),
                personal_data_labels.get(line.sc27k_personal_data_level, ''),
                criteria_values.get('confidentiality', ''),
                criteria_values.get('integrity', ''),
                criteria_values.get('availability', ''),
                criticality_labels.get(line.sc27k_criticality, ''),
                state_labels.get(line.sc27k_asset_state, ''),
                str(line.sc27k_last_review_date or ''),
                str(line.sc27k_next_review_date or ''),
            ]
            is_high_criticality = line.sc27k_criticality == 'high'
            for col, value in enumerate(values):
                if col == _CRITICALITY_COLUMN and is_high_criticality:
                    fmt = critical_format
                elif col in _LEFT_ALIGN_COLUMNS:
                    fmt = left_format
                else:
                    fmt = center_format
                sheet.write(row, col, value, fmt)
            row += 1
