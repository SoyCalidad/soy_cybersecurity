# -*- coding: utf-8 -*-
from odoo import fields, models

# Impact dimensions of the information security risk: the impact of a risk is the MAX of
# these criteria (not their product). Probability is the remaining criterion.
SC27K_IMPACT_CRITERION_TYPES = (
    'confidentiality', 'integrity', 'availability', 'traceability', 'authenticity',
)
SC27K_PROBABILITY_CRITERION_TYPE = 'probability'


class EvaluationCriterio(models.Model):
    _inherit = 'evaluation.criterio'

    # Identifies the role of the criterion in the information security risk formula
    # without relying on its (translatable) name.
    sc27k_criterion_type = fields.Selection(
        selection=[
            ('probability', 'Probability'),
            ('confidentiality', 'Confidentiality'),
            ('integrity', 'Integrity'),
            ('availability', 'Availability'),
            ('traceability', 'Traceability'),
            ('authenticity', 'Authenticity'),
        ],
        string='Information Security Criterion',
    )
