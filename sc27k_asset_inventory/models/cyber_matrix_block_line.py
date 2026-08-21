# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

# Interpretation text used in the existing risk report (mgmtsystem_opportunity/report/
# matrix_report.py): NPA/ntr above 100 is already treated there as the "high" threshold.
_CRITICALITY_HIGH_THRESHOLD = 100
_CRITICALITY_MEDIUM_THRESHOLD = 50


class CyberMatrixBlockLine(models.Model):
    _inherit = 'cyber_matrix.block.line'

    # -------------------------------------------------------------------------
    # 1. Fields Definition
    # -------------------------------------------------------------------------

    sc27k_asset_code = fields.Char(
        string='Código',
        copy=False,
    )
    sc27k_owner_job_id = fields.Many2one(
        'hr.job',
        string='Propietario del activo',
    )
    sc27k_custodian_id = fields.Many2one(
        'hr.employee',
        string='Usuario asignado / Custodio',
    )
    sc27k_ownership = fields.Selection(
        selection=[
            ('corporate', 'Corporativo'),
            ('personal_byod', 'Personal / BYOD'),
            ('third_party', 'Tercero'),
        ],
        string='Titularidad',
    )
    sc27k_information_classification = fields.Selection(
        selection=[
            ('not_applicable', 'No aplica'),
            ('internal', 'Interna'),
            ('restricted', 'Restringida'),
            ('confidential', 'Confidencial'),
        ],
        string='Clasificación de la información',
    )
    sc27k_personal_data_level = fields.Selection(
        selection=[
            ('no', 'No'),
            ('yes', 'Sí'),
            ('may_process', 'Puede procesar'),
            ('may_contain', 'Puede contener'),
        ],
        string='¿Contiene o procesa datos personales?',
    )
    sc27k_asset_state = fields.Selection(
        selection=[
            ('active', 'Activo'),
            ('inactive', 'Inactivo'),
            ('decommissioned', 'Dado de baja'),
        ],
        string='Estado del activo',
        default='active',
    )
    sc27k_last_review_date = fields.Date(string='Última revisión')
    sc27k_next_review_date = fields.Date(string='Próxima revisión')
    sc27k_criticality = fields.Selection(
        selection=[
            ('low', 'Baja'),
            ('medium', 'Media'),
            ('high', 'Alta'),
        ],
        string='Criticidad',
        compute='_sc27k_compute_criticality',
        store=True,
    )

    # -------------------------------------------------------------------------
    # 2. Constraints and Compute Methods
    # -------------------------------------------------------------------------

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
         'El código del activo ya existe para esta compañía.'),
    ]

    # -------------------------------------------------------------------------
    # 7. Helper Methods
    # -------------------------------------------------------------------------
