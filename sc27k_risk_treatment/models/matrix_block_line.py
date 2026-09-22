# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

_SC27K_SECURITY_SYSTEM_XMLID = 'sc27k_base.system_cybersecurity'

# The risk value is Probabilidad x Impacto, where Impacto is the MAX across these five
# dimensions (not their product) — confirmed by the "Formato reporte de riesgos de SI"
# template, which reports each dimension separately plus a single "Impacto inicial"
# column. Matched by evaluation.criterio name.
_SC27K_PROBABILITY_CRITERIA_NAME = 'Probability'
_SC27K_IMPACT_CRITERIA_NAMES = (
    'Confidentiality', 'Integrity', 'Availability', 'Traceability', 'Authenticity',
)

_SC27K_RISK_INTERPRETATION = (
    'The risk level is obtained by multiplying the maximum impact on information '
    'security (max(Confidentiality, Integrity, Availability, Traceability, '
    'Authenticity)) by the realistic probability of occurrence, '
    'resulting in a scale from 1 to 25. Values equal to or greater than 12 (High '
    'or Critical Risk) are unacceptable and require the mandatory implementation of '
    'controls from Annex A of the ISO/IEC 27001:2022 standard and a formal treatment '
    'plan. Values between 5 and 11 (Medium) must be managed or monitored periodically.'
)

# Risk level bands for the Impacto (1-5) x Probabilidad (1-5) indicator, per the
# interpretation text above: <5 Bajo, 5-11 Medio, 12-19 Alto, >=20 Crítico. Only the
# products of two integers in [1, 5] are reachable, so the Alto/Crítico split at 20
# matches every value the 5x5 matrix can actually produce.
_SC27K_RISK_LEVEL_MEDIUM_THRESHOLD = 5
_SC27K_RISK_LEVEL_HIGH_THRESHOLD = 12
_SC27K_RISK_LEVEL_CRITICAL_THRESHOLD = 20

_SC27K_TREATMENT_OPTIONS = [
    ('reduce', 'Reduce'),
    ('avoid', 'Avoid'),
    ('share_transfer', 'Share / Transfer'),
    ('accept', 'Accept'),
]
_SC27K_TREATMENT_STATES = [
    ('pending', 'Pending'),
    ('in_process', 'In Progress'),
    ('implemented', 'Implemented'),
    ('verified', 'Verified'),
]
_SC27K_TREATMENT_APPROVAL_STATES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rework', 'Modification Requested'),
]
_SC27K_RESIDUAL_DECISIONS = [
    ('accept', 'Accept Residual Risk'),
    ('additional_treatment', 'Request Additional Treatment'),
]
_SC27K_RESIDUAL_ACCEPTANCE_STATES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('additional_treatment', 'Additional Treatment Requested'),
]


class MatrixBlockLine(models.Model):
    _inherit = 'matrix.block.line'

    # -------------------------------------------------------------------------
    # 1. Fields Definition
    # -------------------------------------------------------------------------

    sc27k_is_security_profile = fields.Boolean(
        string='Information Security Profile',
        compute='_sc27k_compute_is_security_profile',
        store=True,
    )

    sc27k_asset_id = fields.Many2one(
        'cyber_matrix.block.line',
        string='Asset',
    )
    sc27k_threat = fields.Char(string='Threat')
    sc27k_threat_agent = fields.Char(string='Threat Agent')

    sc27k_initial_ntr = fields.Integer(
        string='Initial Risk Value',
        compute='_sc27k_compute_initial_ntr',
        store=True,
    )
    sc27k_risk_level = fields.Selection(
        selection=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        string='Initial Risk Level',
        compute='_sc27k_compute_risk_levels',
        store=True,
    )
    sc27k_interpretation = fields.Text(
        string='Interpretation',
        default=_SC27K_RISK_INTERPRETATION,
        translate=True,
    )

    sc27k_treatment_option = fields.Selection(
        selection=_SC27K_TREATMENT_OPTIONS,
        string='Treatment Option',
    )
    sc27k_treatment_description = fields.Text(string='Treatment Description')
    sc27k_treatment_responsible_id = fields.Many2one(
        'res.users',
        string='Treatment Responsible',
    )
    sc27k_treatment_start_date = fields.Date(string='Start Date')
    sc27k_treatment_target_date = fields.Date(string='Target Date')
    sc27k_treatment_state = fields.Selection(
        selection=_SC27K_TREATMENT_STATES,
        string='Treatment Status',
        default='pending',
    )

    sc27k_residual_evaluation_id = fields.Many2one(
        'evaluation.evaluation',
        string='Indicator (Residual Evaluation)',
        ondelete='restrict',
    )
    sc27k_residual_result_ids = fields.One2many(
        'evaluation.result',
        inverse_name='sc27k_residual_matrix_block_line_id',
        string='Results (Residual Evaluation)',
        copy=True,
    )
    sc27k_residual_ntr = fields.Integer(
        string='Residual Risk Value',
        compute='_sc27k_compute_residual_ntr',
        store=True,
    )
    sc27k_residual_risk_level = fields.Selection(
        selection=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        string='Residual Risk Level',
        compute='_sc27k_compute_risk_levels',
        store=True,
    )

    sc27k_treatment_owner_id = fields.Many2one('res.users', string='Risk Owner')
    sc27k_treatment_approval_date = fields.Date(string='Treatment Approval Date')
    sc27k_treatment_approval_comment = fields.Text(string='Treatment Approval Comment')
    sc27k_treatment_approved_by_id = fields.Many2one('res.users', string='Approved By')
    sc27k_treatment_approval_state = fields.Selection(
        selection=_SC27K_TREATMENT_APPROVAL_STATES,
        string='Treatment Approval Status',
        default='pending',
    )

    sc27k_residual_decision = fields.Selection(
        selection=_SC27K_RESIDUAL_DECISIONS,
        string='Residual Risk Decision',
    )
    sc27k_residual_accepted_by_id = fields.Many2one('res.users', string='Accepted By')
    sc27k_residual_acceptance_date = fields.Date(string='Residual Risk Acceptance Date')
    sc27k_residual_acceptance_comment = fields.Text(string='Residual Risk Acceptance Comment')
    sc27k_residual_acceptance_state = fields.Selection(
        selection=_SC27K_RESIDUAL_ACCEPTANCE_STATES,
        string='Residual Risk Acceptance Status',
        default='pending',
    )

    # -------------------------------------------------------------------------
    # 2. Constraints and Compute Methods
    # -------------------------------------------------------------------------

    @api.depends('system_id', 'type')
    def _sc27k_compute_is_security_profile(self):
        security_system = self.env.ref(_SC27K_SECURITY_SYSTEM_XMLID, raise_if_not_found=False)
        for record in self:
            record.sc27k_is_security_profile = bool(
                security_system and record.type == 'risk' and record.system_id == security_system
            )

    @api.depends('result_ids', 'result_ids.value', 'result_ids.criterio_id')
    def _sc27k_compute_initial_ntr(self):
        for record in self:
            probability, impact = record._sc27k_extract_probability_and_max_impact(record.result_ids)
            record.sc27k_initial_ntr = probability * impact

    @api.depends('sc27k_residual_result_ids', 'sc27k_residual_result_ids.value',
                 'sc27k_residual_result_ids.criterio_id')
    def _sc27k_compute_residual_ntr(self):
        for record in self:
            probability, impact = record._sc27k_extract_probability_and_max_impact(
                record.sc27k_residual_result_ids)
            record.sc27k_residual_ntr = probability * impact

    @api.depends('sc27k_initial_ntr', 'sc27k_residual_ntr', 'sc27k_is_security_profile')
    def _sc27k_compute_risk_levels(self):
        for record in self:
            if not record.sc27k_is_security_profile:
                record.sc27k_risk_level = False
                record.sc27k_residual_risk_level = False
                continue
            record.sc27k_risk_level = record._sc27k_get_risk_level(record.sc27k_initial_ntr)
            record.sc27k_residual_risk_level = record._sc27k_get_risk_level(record.sc27k_residual_ntr)

    # -------------------------------------------------------------------------
    # 3. Onchange Methods
    # -------------------------------------------------------------------------

    @api.onchange('sc27k_residual_evaluation_id')
    def _sc27k_onchange_residual_evaluation_id(self):
        # Mirrors the base module's create_criterio()/_onchange_evaluation_id(): picking
        # an indicator seeds one empty result line per criterio, ready for the user to
        # fill in a value.
        lines = [(5, 0, 0)]
        for criterio in self.sc27k_residual_evaluation_id.criterio_ids:
            lines.append((0, 0, {
                'criterio_id': criterio.id,
                'name': criterio.name,
                'description': criterio.description,
            }))
        self.sc27k_residual_result_ids = lines

    # -------------------------------------------------------------------------
    # 4. Action Methods
    # -------------------------------------------------------------------------

    def sc27k_action_approve_treatment(self):
        self.write({
            'sc27k_treatment_approval_state': 'approved',
            'sc27k_treatment_approved_by_id': self.env.user.id,
            'sc27k_treatment_approval_date': fields.Date.context_today(self),
        })

    def sc27k_action_request_treatment_rework(self):
        self.write({'sc27k_treatment_approval_state': 'rework'})

    def sc27k_action_accept_residual_risk(self):
        self.write({
            'sc27k_residual_decision': 'accept',
            'sc27k_residual_acceptance_state': 'accepted',
            'sc27k_residual_accepted_by_id': self.env.user.id,
            'sc27k_residual_acceptance_date': fields.Date.context_today(self),
        })

    def sc27k_action_request_additional_treatment(self):
        self.write({
            'sc27k_residual_decision': 'additional_treatment',
            'sc27k_residual_acceptance_state': 'additional_treatment',
        })

    # -------------------------------------------------------------------------
    # 5. Overrides and Business Logic
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # 6. SQL Constraints
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # 7. Helper Methods
    # -------------------------------------------------------------------------

    def _sc27k_get_risk_level(self, ntr):
        """Map a 1-25 Impacto x Probabilidad score to its risk band."""
        self.ensure_one()
        if ntr >= _SC27K_RISK_LEVEL_CRITICAL_THRESHOLD:
            return 'critical'
        if ntr >= _SC27K_RISK_LEVEL_HIGH_THRESHOLD:
            return 'high'
        if ntr >= _SC27K_RISK_LEVEL_MEDIUM_THRESHOLD:
            return 'medium'
        return 'low'

    def _sc27k_extract_probability_and_max_impact(self, results):
        """Return (probability_value, max_impact_value) from an evaluation.result
        recordset, matched by criterio name. Missing criteria contribute 0, so a
        partially-filled evaluation yields a value of 0 rather than raising.
        """
        self.ensure_one()
        probability = 0
        impact = 0
        for result in results:
            criterio_name = result.criterio_id.name
            if criterio_name == _SC27K_PROBABILITY_CRITERIA_NAME:
                probability = result.value
            elif criterio_name in _SC27K_IMPACT_CRITERIA_NAMES:
                impact = max(impact, result.value)
        return probability, impact
