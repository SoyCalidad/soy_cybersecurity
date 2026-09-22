from odoo import api, fields, models


class MatrixMatrix(models.Model):
    _inherit = 'cyber_2matrix.matrix'

    elaboration_step = fields.One2many(
        'mgmtsystem.validation.step', 'cyber_2matrix_elaboration_id', string='Elaboration')
    review_step = fields.One2many(
        'mgmtsystem.validation.step', 'cyber_2matrix_review_id', string='Review')
    validation_step = fields.One2many(
        'mgmtsystem.validation.step', 'cyber_2matrix_validation_id', string='Validation')

    process_id = fields.Many2one(
        'process.edition',
        string='Procedure',
        domain=[('active', '=', True)],
        ondelete='set null'
    )


class MatrixValidation(models.Model):
    _inherit = 'mgmtsystem.validation.step'

    cyber_2matrix_elaboration_id = fields.Many2one(
        'cyber_2matrix.matrix',
        string='Cyber Matrix Elaboration',
        ondelete='set null'
    )
    cyber_2matrix_review_id = fields.Many2one(
        'cyber_2matrix.matrix', string='Cyber Matrix Review', ondelete='set null')
    cyber_2matrix_validation_id = fields.Many2one(
        'cyber_2matrix.matrix', string='Cyber Matrix Validation', ondelete='set null')


class MatrixBlockLine(models.Model):
    _inherit = 'cyber_2matrix.block.line'

    def button_new_version(self):
        super().button_new_version()
        self.state = 'draft'
