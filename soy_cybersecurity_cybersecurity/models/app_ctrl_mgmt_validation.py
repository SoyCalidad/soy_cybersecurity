from odoo import api, fields, models


class MatrixMatrix(models.Model):
    _inherit = 'cyber_2matrix.matrix'

    elaboration_step = fields.One2many(
        'mgmtsystem.validation.step', 'cyber_2matrix_elaboration_id', string='Elaboración')
    review_step = fields.One2many(
        'mgmtsystem.validation.step', 'cyber_2matrix_review_id', string='Revisión')
    validation_step = fields.One2many(
        'mgmtsystem.validation.step', 'cyber_2matrix_validation_id', string='Validación')

    process_id = fields.Many2one(
        'process.edition', string='Procedimiento', domain=[('active','=',True)])


class MatrixValidation(models.Model):
    _inherit = 'mgmtsystem.validation.step'

    cyber_2matrix_elaboration_id = fields.Many2one(
        'cyber_2matrix.matrix', string='Padre')
    cyber_2matrix_review_id = fields.Many2one(
        'cyber_2matrix.matrix', string='Padre')
    cyber_2matrix_validation_id = fields.Many2one(
        'cyber_2matrix.matrix', string='Padre')


class MatrixBlockLine(models.Model):
    _inherit = 'cyber_2matrix.block.line'

    def button_new_version(self):
        super().button_new_version()
        self.state = 'draft'
