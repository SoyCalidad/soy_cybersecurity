# -*- coding: utf-8 -*-
from odoo import fields, models


class EvaluationResult(models.Model):
    _inherit = 'evaluation.result'

    sc27k_residual_matrix_block_line_id = fields.Many2one(
        'matrix.block.line',
        string='Registro de matriz (evaluación residual)',
        ondelete='cascade',
    )
