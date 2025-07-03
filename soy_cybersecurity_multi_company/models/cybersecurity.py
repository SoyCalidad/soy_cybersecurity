from odoo import api, fields, models


class Categ(models.Model):
    _inherit = 'cyber_2matrix.categ'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class Matrix(models.Model):
    _inherit = 'cyber_2matrix.matrix'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class Block(models.Model):
    _inherit = 'cyber_2matrix.block'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class Checklist(models.Model):
    _inherit = 'cyber_2matrix.checklist'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class ChecklistControl(models.Model):
    _inherit = 'cyber_2matrix.checklist.control'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class ChecklistLine(models.Model):
    _inherit = 'cyber_2matrix.checklist.line'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class Line(models.Model):
    _inherit = 'cyber_2matrix.block.line'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class CyberMatrixCateg(models.Model):
    _inherit = 'cyber_matrix.categ'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class CyberMatrixMatrix(models.Model):
    _inherit = 'cyber_matrix.matrix'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class CyberMatrixBlock(models.Model):
    _inherit = 'cyber_matrix.block'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class LineAgent(models.Model):
    _inherit = 'cyber_matrix.block.line.agent'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class CyberMatrixBlockLineSystem(models.Model):
    _inherit = 'cyber_matrix.block.line.system'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class CyberMatrixBlockLineResource(models.Model):
    _inherit = 'cyber_matrix.block.line.resource'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class CyberMatrixBlockLineLocation(models.Model):
    _inherit = 'cyber_matrix.block.line.location'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class MatrixBlockLineSystem(models.Model):
    _inherit = 'cyber_matrix.block.line.language'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class CyberMatrixBlockLine(models.Model):
    _inherit = 'cyber_matrix.block.line'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class Result(models.Model):
    _inherit = 'cyber_evaluation.result'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class incidentCateg(models.Model):
    _inherit = 'incident.categ'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class incidentVia(models.Model):
    _inherit = 'incident.via'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class incidentQuickAction(models.Model):
    _inherit = 'incident.quick.action'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)


class incident(models.Model):
    _inherit = 'incident.incident'

    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company)
