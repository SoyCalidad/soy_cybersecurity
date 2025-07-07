from odoo import api, fields, models


class MatrixMatrix(models.Model):
    _inherit = 'cyber_matrix.matrix'

    elaboration_step = fields.One2many(
        'mgmtsystem.validation.step', 'matrix_elaboration_id', string='Elaboración')
    review_step = fields.One2many(
        'mgmtsystem.validation.step', 'matrix_review_id', string='Revisión')
    validation_step = fields.One2many(
        'mgmtsystem.validation.step', 'matrix_validation_id', string='Validación')

    process_id = fields.Many2one(
        'process.edition', string='Procedimiento', domain=[('active','=',True)],  ondelete='set null')


# This is mgmtsystem_opportunity module
# class MatrixValidation(models.Model):
#     _inherit = 'mgmtsystem.validation.step'

#     matrix_elaboration_id = fields.Many2one(
#         'cyber_matrix.matrix', string='Padre', ondelete='set null')
#     matrix_review_id = fields.Many2one(
#         'cyber_matrix.matrix', string='Padre', ondelete='set null')
#     matrix_validation_id = fields.Many2one(
#         'cyber_matrix.matrix', string='Padre', ondelete='set null')


class MatrixBlockLine(models.Model):
    _inherit = 'cyber_matrix.block.line'

    def button_new_version(self):
        super().button_new_version()
        self.state = 'draft'
