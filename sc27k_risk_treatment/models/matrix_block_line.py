# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

_SC27K_SECURITY_SYSTEM_XMLID = 'sc27k_base.system_cybersecurity'

# The risk value is Probabilidad x Impacto, where Impacto is the MAX across these five
# dimensions (not their product) — confirmed by the "Formato reporte de riesgos de SI"
# template, which reports each dimension separately plus a single "Impacto inicial"
# column. Matched by evaluation.criterio name.
_SC27K_PROBABILITY_CRITERIA_NAME = 'Probabilidad'
_SC27K_IMPACT_CRITERIA_NAMES = (
    'Confidencialidad', 'Integridad', 'Disponibilidad', 'Trazabilidad', 'Autenticidad',
)

_SC27K_RISK_INTERPRETATION = (
    'El nivel de riesgo se obtiene multiplicando el impacto máximo sobre la seguridad '
    'de la información (max(Confidencialidad, Integridad, Disponibilidad, Trazabilidad, '
    'Autenticidad)) por la probabilidad realista de ocurrencia, '
    'resultando en una escala de 1 a 25. Valores iguales o superiores a 12 (Riesgo Alto '
    'o Crítico) son inaceptables y requieren la implementación obligatoria de controles '
    'del Anexo A de la norma ISO/IEC 27001:2022 y un plan de tratamiento formal. Valores '
    'entre 5 y 11 (Medio) deben ser gestionados o monitoreados periódicamente.'
)

# Risk level bands for the Impacto (1-5) x Probabilidad (1-5) indicator, per the
# interpretation text above: <5 Bajo, 5-11 Medio, 12-19 Alto, >=20 Crítico. Only the
# products of two integers in [1, 5] are reachable, so the Alto/Crítico split at 20
# matches every value the 5x5 matrix can actually produce.
_SC27K_RISK_LEVEL_MEDIUM_THRESHOLD = 5
_SC27K_RISK_LEVEL_HIGH_THRESHOLD = 12
_SC27K_RISK_LEVEL_CRITICAL_THRESHOLD = 20

_SC27K_TREATMENT_OPTIONS = [
    ('reduce', 'Reducir'),
    ('avoid', 'Evitar'),
    ('share_transfer', 'Compartir / Transferir'),
    ('accept', 'Aceptar'),
]
_SC27K_TREATMENT_STATES = [
    ('pending', 'Pendiente'),
    ('in_process', 'En proceso'),
    ('implemented', 'Implementado'),
    ('verified', 'Verificado'),
]
_SC27K_TREATMENT_APPROVAL_STATES = [
    ('pending', 'Pendiente'),
    ('approved', 'Aprobado'),
    ('rework', 'Modificación solicitada'),
]
_SC27K_RESIDUAL_DECISIONS = [
    ('accept', 'Aceptar riesgo residual'),
    ('additional_treatment', 'Solicitar tratamiento adicional'),
]
_SC27K_RESIDUAL_ACCEPTANCE_STATES = [
    ('pending', 'Pendiente'),
    ('accepted', 'Aceptado'),
    ('additional_treatment', 'Tratamiento adicional solicitado'),
]


class MatrixBlockLine(models.Model):
    _inherit = 'matrix.block.line'

    # -------------------------------------------------------------------------
    # 1. Fields Definition
    # -------------------------------------------------------------------------

    sc27k_is_security_profile = fields.Boolean(
        string='Perfil de seguridad de la información',
        compute='_sc27k_compute_is_security_profile',
        store=True,
    )

    sc27k_asset_id = fields.Many2one(
        'cyber_matrix.block.line',
        string='Activo',
    )
    sc27k_threat = fields.Char(string='Amenaza')
    sc27k_threat_agent = fields.Char(string='Agente de la amenaza')

    sc27k_initial_ntr = fields.Integer(
        string='Valor de riesgo inicial',
        compute='_sc27k_compute_initial_ntr',
        store=True,
    )
    sc27k_risk_level = fields.Selection(
        selection=[
            ('low', 'Bajo'),
            ('medium', 'Medio'),
            ('high', 'Alto'),
            ('critical', 'Crítico'),
        ],
        string='Nivel de riesgo inicial',
        compute='_sc27k_compute_risk_levels',
        store=True,
    )
    sc27k_interpretation = fields.Text(
        string='Interpretación',
        default=_SC27K_RISK_INTERPRETATION,
        translate=True,
    )

    sc27k_treatment_option = fields.Selection(
        selection=_SC27K_TREATMENT_OPTIONS,
        string='Opción de tratamiento',
    )
    sc27k_treatment_description = fields.Text(string='Descripción del tratamiento')
    sc27k_treatment_responsible_id = fields.Many2one(
        'res.users',
        string='Responsable del tratamiento',
    )
    sc27k_treatment_start_date = fields.Date(string='Fecha de inicio')
    sc27k_treatment_target_date = fields.Date(string='Fecha objetivo')
    sc27k_treatment_state = fields.Selection(
        selection=_SC27K_TREATMENT_STATES,
        string='Estado del tratamiento',
        default='pending',
    )

    sc27k_residual_evaluation_id = fields.Many2one(
        'evaluation.evaluation',
        string='Indicador (evaluación residual)',
        ondelete='restrict',
    )
    sc27k_residual_result_ids = fields.One2many(
        'evaluation.result',
        inverse_name='sc27k_residual_matrix_block_line_id',
        string='Resultados (evaluación residual)',
        copy=True,
    )
    sc27k_residual_ntr = fields.Integer(
        string='Valor de riesgo residual',
        compute='_sc27k_compute_residual_ntr',
        store=True,
    )
    sc27k_residual_risk_level = fields.Selection(
        selection=[
            ('low', 'Bajo'),
            ('medium', 'Medio'),
            ('high', 'Alto'),
            ('critical', 'Crítico'),
        ],
        string='Nivel de riesgo residual',
        compute='_sc27k_compute_risk_levels',
        store=True,
    )

    sc27k_treatment_owner_id = fields.Many2one('res.users', string='Propietario del riesgo')
    sc27k_treatment_approval_date = fields.Date(string='Fecha de aprobación del tratamiento')
    sc27k_treatment_approval_comment = fields.Text(string='Comentario de aprobación del tratamiento')
    sc27k_treatment_approved_by_id = fields.Many2one('res.users', string='Aprobado por')
    sc27k_treatment_approval_state = fields.Selection(
        selection=_SC27K_TREATMENT_APPROVAL_STATES,
        string='Estado de aprobación del tratamiento',
        default='pending',
    )

    sc27k_residual_decision = fields.Selection(
        selection=_SC27K_RESIDUAL_DECISIONS,
        string='Decisión sobre el riesgo residual',
    )
    sc27k_residual_accepted_by_id = fields.Many2one('res.users', string='Aceptado por')
    sc27k_residual_acceptance_date = fields.Date(string='Fecha de aceptación del riesgo residual')
    sc27k_residual_acceptance_comment = fields.Text(string='Comentario de aceptación del riesgo residual')
    sc27k_residual_acceptance_state = fields.Selection(
        selection=_SC27K_RESIDUAL_ACCEPTANCE_STATES,
        string='Estado de aceptación del riesgo residual',
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
