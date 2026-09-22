# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

# Interpretation text used in the existing risk report (mgmtsystem_opportunity/report/
# matrix_report.py): NPA/ntr above 100 is already treated there as the "high" threshold.
_CRITICALITY_HIGH_THRESHOLD = 100
_CRITICALITY_MEDIUM_THRESHOLD = 50

_SC27K_SECURITY_SYSTEM_XMLID = 'sc27k_base.system_cybersecurity'

# MAGERIT asset type taxonomy, requested verbatim (code + label) for the ISO 27001
# security profile — a fixed list, distinct from the generic free-form asset_type_id
# used by non-security clients of this inventory.
_SC27K_ASSET_TYPES = [
    ('D', '[D] Data / Information'),
    ('K', '[K] Cryptographic keys'),
    ('S', '[S] Services'),
    ('SW', '[SW] Software'),
    ('HW', '[HW] Hardware'),
    ('COM', '[COM] Communication networks'),
    ('MEDIA', '[Media] Information media'),
    ('AUX', '[AUX] Auxiliary equipment'),
    ('L', '[L] Facilities'),
    ('P', '[P] Personnel'),
]


class Sc27kCategory(models.Model):
    _name = 'sc27k.asset.inventory.category'
    _description = 'Asset Inventory Category'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
    )

    active = fields.Boolean(
        string='Active',
        default=True,
    )

class CyberMatrixBlockLine(models.Model):
    _inherit = 'cyber_matrix.block.line'

    # -------------------------------------------------------------------------
    # 1. Fields Definition
    # -------------------------------------------------------------------------

    sc27k_is_security_profile = fields.Boolean(
        string='Information Security Profile',
        compute='_sc27k_compute_is_security_profile',
        store=True,
    )
    sc27k_asset_code = fields.Char(
        string='Code',
        copy=False,
    )
    sc27k_asset_type = fields.Selection(
        selection=_SC27K_ASSET_TYPES,
        string='Asset Type',
    )
    sc27k_owner_job_id = fields.Many2one(
        'hr.job',
        string='Asset Owner',
    )
    sc27k_custodian_id = fields.Many2one(
        'hr.employee',
        string='Assigned User / Custodian',
    )
    sc27k_ownership = fields.Selection(
        selection=[
            ('corporate', 'Corporate'),
            ('personal_byod', 'Personal / BYOD'),
            ('third_party', 'Third Party'),
        ],
        string='Ownership',
    )
    sc27k_information_classification = fields.Selection(
        selection=[
            ('not_applicable', 'Not Applicable'),
            ('internal', 'Internal'),
            ('restricted', 'Restricted'),
            ('confidential', 'Confidential'),
        ],
        string='Information Classification',
    )
    sc27k_personal_data_level = fields.Selection(
        selection=[
            ('no', 'No'),
            ('yes', 'Yes'),
            ('may_process', 'May process'),
            ('may_contain', 'May contain'),
        ],
        string='Contains or Processes Personal Data?',
    )
    sc27k_asset_state = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('decommissioned', 'Decommissioned'),
        ],
        string='Asset Status',
        default='active',
    )
    sc27k_last_review_date = fields.Date(string='Last Review')
    sc27k_next_review_date = fields.Date(string='Next Review')
    sc27k_criticality = fields.Selection(
        selection=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
        ],
        string='Criticality',
        compute='_sc27k_compute_criticality',
        store=True,
    )
    sc27k_security_certification = fields.Selection(
        selection=[
            ('yes', 'Yes'),
            ('no', 'No'),
            ('not_applicable', 'Not Applicable'),
        ],
        string='Has Security Certification?',
    )

    sc27k_category_ids = fields.Many2many(
        'sc27k.asset.inventory.category',
        string='Category',
    )

    # -------------------------------------------------------------------------
    # 2. Constraints and Compute Methods
    # -------------------------------------------------------------------------

    @api.depends('system_id')
    def _sc27k_compute_is_security_profile(self):
        security_system = self.env.ref(_SC27K_SECURITY_SYSTEM_XMLID, raise_if_not_found=False)
        for record in self:
            record.sc27k_is_security_profile = bool(
                security_system and record.system_id == security_system
            )

    @api.depends('ntr')
    def _sc27k_compute_criticality(self):
        for record in self:
            if record.ntr > _CRITICALITY_HIGH_THRESHOLD:
                record.sc27k_criticality = 'high'
            elif record.ntr > _CRITICALITY_MEDIUM_THRESHOLD:
                record.sc27k_criticality = 'medium'
            else:
                record.sc27k_criticality = 'low'

    # -------------------------------------------------------------------------
    # 3. Onchange Methods
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # 4. Action Methods
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # 5. Overrides and Business Logic
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # 6. SQL Constraints
    # -------------------------------------------------------------------------

    _sql_constraints = [
        ('sc27k_asset_code_company_uniq', 'unique(sc27k_asset_code, company_id)',
         _('The asset code already exists for this company.')),
    ]

    # -------------------------------------------------------------------------
    # 7. Helper Methods
    # -------------------------------------------------------------------------
