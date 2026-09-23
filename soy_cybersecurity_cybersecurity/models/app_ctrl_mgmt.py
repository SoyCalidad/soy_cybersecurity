# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError

class Categ(models.Model):
    _name = 'cyber_2matrix.categ'
    _description = "Categoria de matriz"

    name = fields.Char(
        string=u'Name',
        required=True,
    )
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company,
    )
    
    sequence_id = fields.Many2one(
        string=u'Secuencia de ediciones',
        comodel_name='ir.sequence',
        ondelete='cascade',
    )

    matrix_ids = fields.One2many(
        string='Matrices',
        comodel_name='cyber_2matrix.matrix',
        inverse_name='categ_id',
    )

    @api.onchange('name')
    def _onchange_name(self):
        if self.sequence_id:
            self.sequence_id.name = 'Secuencia de '+self.name

    @api.model_create_multi
    def create(self, values_list):
        for values in values_list:
            sequence = self.env['ir.sequence'].sudo().create({
                'name': 'Secuencia de '+values.get('name'),
                'active': True,
                'prefix': 'Edición-nro.',
                'padding': 4,
                'number_next': 1,
                'number_increment': 1,
            })
            
            values['sequence_id'] = sequence.id
        results = super(Categ, self).create(values_list)
        return results

    def unlink(self):
        for categ in self:
            categ.sequence_id.unlink()
        return super(Categ, self).unlink()

class MatrixLine(models.Model):
    _name = 'cyber_2matrix.matrix.line'
    _description = "Lineas de la Matrix de declaración de aplicabilidad"

    applicability_id = fields.Many2one(
        comodel_name='cyber_2matrix.block.line',
        string="Applicability",
        required=True,
    )
    justification  = fields.Text(string="Justification for applicability / non-applicability")
    reference  = fields.Text(string="Control implementation reference")
    is_implemented = fields.Selection(
        selection=[
            ('no', 'No'),
            ('yes', 'Yes'),
        ],
        default='no', 
        string="Control implemented?")

    applicability_id_name = fields.Char(
        related='applicability_id.name',
        string="Control name",
    )
    applicability_id_domain_id = fields.Many2one(
        related='applicability_id.domain_id',
    )
    applicability_id_description_application = fields.Text(
        related='applicability_id.description_application',
        string="Control description",
    )
    # applicability_id_application = fields.Boolean(
    #     related='applicability_id.application',
    #     string="Aplicabilidad",
    # )
    application = fields.Selection(
        selection=[
            ('no', 'No'),
            ('yes', 'Yes'),
        ],
        string='Applicability', default='no')

    action_ids = fields.Many2many(
        comodel_name='mgmtsystem.action',
        string="Actions",
    )

    matrix_id = fields.Many2one(
        'cyber_2matrix.matrix',
        required=True,
        ondelete='cascade',
    )



class Matrix(models.Model):
    _name = 'cyber_2matrix.matrix'
    _inherit = ['mgmtsystem.validation.mail', 'mgmtsystem.code']
    _description = "Applicability Statement Matrix"

    parent_edition = fields.Many2one(
        comodel_name='cyber_2matrix.matrix', string='Parent', copy=False)
    old_versions = fields.One2many(
        comodel_name='cyber_2matrix.matrix', string='Old Versions',
        inverse_name='parent_edition', context={'active_version': False})

    def action_open_older_versions(self):
        result = self.env.ref(
            'soy_cybersecurity_cybersecurity.matrix_matrix_app_ctrl_mgmt_action').read()[0]
        result['domain'] = [('id', 'in', self.old_versions.ids)]
        # result['context'] = {'active_version': False, 'type': self.type}
        return result

    name = fields.Char(
        string='Matrix Name',
    )
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    numero = fields.Char(
        string="Sequence Number",
        readonly=True,
        required=True,
        copy=False,
        default=lambda self: _('Undefined'),
    )

    categ_id = fields.Many2one(
        string='Matrix Name',
        comodel_name='cyber_2matrix.categ',
        ondelete='cascade',
    )
    system_id = fields.Many2one(
        'mgmtsystem.context.system', string='Risk Identifier', default=lambda self: self.env.ref('hola_calidad.policy_system_1'))

    @api.onchange('categ_id')
    def _onchange_categ_id(self):
        if self.categ_id:
            self.name = self.categ_id.name + " " + self.numero


    sequence_id = fields.Many2one(
        string='Edition Sequence',
        comodel_name='ir.sequence',
        related='categ_id.sequence_id',
    )

    date_elaborate = fields.Datetime(
        string='Elaboration Date',
        default=fields.Datetime.now,
        readonly=True,
        store=True,
    )

    date_review = fields.Datetime(
        string='Review Date',
        default=fields.Datetime.now,
        readonly=True,
        store=True,
    )

    user_ids = fields.Many2many(
        string='Validated By',
        comodel_name='res.users',
        relation='cyber_2matrix_users_rel',
        column1='user_id',
        column2='matrix_id',
    )

    date_validate = fields.Datetime(
        string='Validation Date',
        readonly=True,
        store=True,
    )

    filter = fields.Selection(
        string='Filter By',
        selection=[
            ('none', 'All Pending Lines'),
            ('date', 'Between Creation Date Range'),
            ('block', 'By Sources'),
            ('state', 'Risk State'),
            ('partial', 'Select Manually')],
        default='none',
    )

    date_init = fields.Date(
        string='Start Date',
    )
    date_fin = fields.Date(
        string='End Date',
    )

    block_ids = fields.Many2many(
        string='Sources',
        comodel_name='cyber_2matrix.block',
        relation='cyber_2matrix_block_line_rel',
        column1='block_id',
        column2='matrix_id',
    )

    state = fields.Selection(
        string='State',
        selection=[
            ('elaborate', 'In Progress'),
            ('review', 'In Review'),
            ('validate', 'In Validation'),
            ('validate_ok', 'Validated'),
            ('cancel', 'Cancelled')],
        default='elaborate',
    )
    state_line = fields.Selection(
        string='Line State',
        selection=[
            ('draft', 'Draft'),
            ('elaborate', 'In Progress'),
            ('validate', 'Validated'),
            ('cancel', 'Cancelled')],
    )

    line_ids = fields.One2many(
        'cyber_2matrix.matrix.line',
        'matrix_id',
    )

    def send_elaborate(self):
        self.state = 'elaborate'

    def send_elaborate_o(self):
        # self.exec_filter()
        self.state = 'elaborate'

    def create_action(self, vuser_id):
        action = self.env.ref('hola_calidad.p_mail_activity_action').read()[0]
        self.env.cr.execute("""SELECT id FROM ir_model 
                                  WHERE model = %s""", (str(self._name),))
        info = self.env.cr.dictfetchall()
        model_id = False
        if info:
            model_id = info[0]['id']
        action['context'] = {
            'default_res_id': self.ids[0],
            'default_res_model': self._name,
            'default_res_model_id': model_id,
            'default_user_id': vuser_id,
        }
        return action

    def unlink(self):
        for matrix in self:
            if matrix.state not in ['draft', 'elaborate']:
                raise ValidationError(
                    _('Deleting records is only allowed in draft and in progress states'))
        return super(Matrix, self).unlink()

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        if 'line_ids' in fields_list:
            applicability_ids = self.env['cyber_2matrix.block.line'].search([], order='sequence').ids
            res['line_ids'] = [
                (0, 0, {
                    'applicability_id': applicability_id,
                    'is_implemented': False,
                })
                for applicability_id in applicability_ids
            ]

        return res


class Block(models.Model):
    _name = 'cyber_2matrix.block'
    _description = "Source"

    name = fields.Char(
        string='Source',
    )
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company,
    )

    @api.onchange('process_id')
    def _onchange_process_id(self):
        if self.process_id:
            self.name = self.process_id.process_id.name

    @api.onchange('other')
    def _onchange_other(self):
        self.name = self.other

    process_id = fields.Many2one(
        string='Process',
        comodel_name='process.edition',
        ondelete='cascade',
        domain=[('active', '=', True)]
    )
    other = fields.Char(
        string='Other',
    )

    line_ids = fields.One2many(
        string='Lines',
        comodel_name='cyber_2matrix.block.line',
        inverse_name='block_id',
    )

    state = fields.Selection(
        string='State',
        selection=[
            ('draft', 'Draft'),
            ('elaborate', 'In Progress'),
            ('validate', 'Validated'),
            ('cancel', 'Cancelled')],
        default='draft',
    )

    def send_elaborate(self):
        self.state = 'elaborate'

    def send_validate(self):
        self.state = 'validate'
        for line in self.line_ids:
            line.send_validate()

    def send_cancel(self):
        self.state = 'cancel'
        for line in self.line_ids:
            line.send_cancel()


class CyberMatrixBlockLineDomain(models.Model):
    _name = 'cyber_2matrix.block.line.domain'
    _description = 'Domain'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')

    ctrl_target_id = fields.One2many(
        string='Control Objectives',
        comodel_name='cyber_2matrix.block.line.ctrl_target',
        inverse_name='domain_id',
    )


class CyberMatrixBlockLineCtrlTarget(models.Model):
    _name = 'cyber_2matrix.block.line.ctrl_target'
    _description = 'Control Objective'

    name = fields.Char(string='Name')
    domain_id = fields.Many2one('cyber_2matrix.block.line.domain', string='Domain')


class Checklist(models.Model):
    _name = 'cyber_2matrix.checklist'
    _inherit = ['mgmtsystem.version', 'mail.thread', 'mail.activity.mixin', 'mgmtsystem.code']
    _description = "Checklist"

    name = fields.Char('Name')
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Validated'),
        ('cancel', 'Cancelled'),
    ], default='draft', string='State')
    line_ids = fields.One2many('cyber_2matrix.checklist.line', 'checklist_id', string='Lines')

    def action_send_validate(self):
        self.state = 'validate'

    def action_send_cancel(self):
        self.state = 'cancel'

    @api.model
    def default_get(self, fields_list):
        defaults = super(Checklist, self).default_get(fields_list)
        control_records = self.env['cyber_2matrix.checklist.control'].search([])
        line_values = [(0, 0, {'checklist_control_id': control.id}) for control in control_records]
        if 'line_ids' in fields_list:
            defaults['line_ids'] = line_values
        return defaults


class ChecklistControl(models.Model):
    _name = 'cyber_2matrix.checklist.control'
    _description = "Checklist Control"
    _order = 'sequence, id'
    _rec_name = 'number'

    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company,
    )
    sequence = fields.Integer(default=10)
    number = fields.Char('Number')
    number_compute = fields.Char('Number', compute='_compute_number')
    description = fields.Char('Description')
    control = fields.Text('Control')

    @api.depends('number')
    def _compute_number(self):
        for each in self:
            each.number_compute = each.number


class ChecklistLine(models.Model):
    _name = 'cyber_2matrix.checklist.line'
    _description = "Checklist Line"
    _rec_name = 'checklist_control_id'

    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company,
    )
    checklist_id = fields.Many2one('cyber_2matrix.checklist', string='Checklist')
    checklist_control_id = fields.Many2one('cyber_2matrix.checklist.control', string='Number')
    checklist_control_number = fields.Char(related='checklist_control_id.number_compute', string='Number')
    checklist_control_description = fields.Char(related='checklist_control_id.description', string='Description')
    checklist_control_control = fields.Text(related='checklist_control_id.control', string='Control')
    applies = fields.Boolean('Applies', default=False)
    documentary_control_ids = fields.Many2many('documentary.control', string='Documents')
    comments = fields.Text('Comments')


class Line(models.Model):
    _name = 'cyber_2matrix.block.line'
    _inherit = ['mgmtsystem.version', 'mail.thread',
                'mail.activity.mixin', 'mgmtsystem.code']
    _description = "Applicability Statement"

    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company,
    )
    parent_edition = fields.Many2one(
        comodel_name='cyber_2matrix.block.line', string='Parent', copy=False)
    old_versions = fields.One2many(
        comodel_name='cyber_2matrix.block.line', string='Old Versions',
        inverse_name='parent_edition', context={'active_version': False})

    def action_open_older_versions(self):
        result = self.env.ref(
            'mgmtsystem_opportunity.matrix_block_line_risk_action').read()[0]
        result['domain'] = [('id', 'in', self.old_versions.ids)]
        # result['context'] = {'active_version': False, 'type': self.type}
        return result

    active = fields.Boolean(default=True, string="Active")
    sequence = fields.Integer(default=1, string="#")
    name = fields.Char(
        string='Name',
        required=True,
    )
    block_id = fields.Many2one(
        string='Source',
        comodel_name='cyber_2matrix.block',
        ondelete='restrict',
    )
    user_id = fields.Many2one(comodel_name='res.users', string='Responsible')

    system_id = fields.Many2one(
        'mgmtsystem.context.system', string='Identifier', default=lambda self: self.env.ref('hola_calidad.policy_system_1'))
    process_id = fields.Many2one('mgmt.categ', string='Process')

    description = fields.Text(
        string='Description',
    )

    domain_id = fields.Many2one('cyber_2matrix.block.line.domain', string='Domain')
    domain_description = fields.Text(related='domain_id.description', readonly=True, string='Domain Description')

    ctrl_target_id = fields.Many2one('cyber_2matrix.block.line.ctrl_target', string='Control Objective')

    @api.onchange('domain_id')
    def _onchange_domain_id(self):
        if self.domain_id:
            return {'domain': {'ctrl_target_id': [('domain_id', '=', self.domain_id.id)]}}
        else:
            return {'domain': {'ctrl_target_id': []}}

    @api.constrains('ctrl_target_id', 'domain_id')
    def _check_ctrl_target(self):
        if self.ctrl_target_id and self.domain_id and self.ctrl_target_id.domain_id != self.domain_id:
            raise ValidationError(_("The selected Control Objective does not belong to the specified domain."))

    application = fields.Boolean(string='Applicability', default=False)
    description_application = fields.Text(string='Application Description')

    implementation_record = fields.Text(string='Implementation Evidence or Record')
    type = fields.Selection(
        string='Type',
        selection=[
            ('national', 'National'),
            ('international', 'International')],
    )

    action_ids = fields.Many2many(
        string='Actions',
        comodel_name='mgmtsystem.action',
        relation='cyber2_block_line_action_rel',
        column1='action_id',
        column2='line_id',
    )

    state = fields.Selection(
        string='State',
        selection=[
            ('draft', 'Draft'),
            ('validate', 'Validated'),
            ('cancel', 'Cancelled')],
        default='draft',
    )


    # def send_elaborate(self):
    #     self.state = 'elaborate'

    def send_validate(self):
        self.state = 'validate'

    def send_cancel(self):
        self.state = 'cancel'