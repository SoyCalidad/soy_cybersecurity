# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError

class Categ(models.Model):
    _name = 'cyber_2matrix.categ'
    _description = "Categoria de matriz"

    name = fields.Char(
        string=u'Nombre',
        required=True,
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

    @api.model
    def create(self, values):
        sequence = self.env['ir.sequence'].create({
            'name': 'Secuencia de '+values.get('name'),
            'active': True,
            'prefix': 'Edición-nro.',
            'padding': 4,
            'number_next': 1,
            'number_increment': 1,
        })
        values['sequence_id'] = sequence.id
        result = super(Categ, self).create(values)
        return result

    def unlink(self):
        for categ in self:
            categ.sequence_id.unlink()
        return super(Categ, self).unlink()


class Matrix(models.Model):
    _name = 'cyber_2matrix.matrix'
    _inherit = ['mgmtsystem.validation.mail', 'mgmtsystem.code']
    _description = "Matriz"

    parent_edition = fields.Many2one(
        comodel_name='cyber_2matrix.matrix', string='Padre', copy=False)
    old_versions = fields.One2many(
        comodel_name='cyber_2matrix.matrix', string='Versiones antiguas',
        inverse_name='parent_edition', context={'active_version': False})

    def action_open_older_versions(self):
        result = self.env.ref(
            'mgmtsystem_opportunity.matrix_matrix_risk_action').read()[0]
        result['domain'] = [('id', 'in', self.old_versions.ids)]
        #result['context'] = {'active_version': False, 'type': self.type}
        return result

    name = fields.Char(
        string='Nombre de matriz',
    )

    numero = fields.Char(
        string="Numero de secuencia",
        readonly=True,
        required=True,
        copy=False,
        default='Sin definir',
    )

    categ_id = fields.Many2one(
        string=u'Nombre de matríz',
        comodel_name='cyber_2matrix.categ',
        ondelete='cascade',
    )
    system_id = fields.Many2one(
        'mgmtsystem.context.system', string='Identificador de riesgo', default=lambda self: self.env.ref('hola_calidad.policy_system_1'))

    @api.onchange('categ_id')
    def _onchange_categ_id(self):
        if self.categ_id:
            self.name = self.categ_id.name + " " + self.numero


    sequence_id = fields.Many2one(
        string=u'Secuencia de ediciones',
        comodel_name='ir.sequence',
        related='categ_id.sequence_id',
    )

    date_elaborate = fields.Datetime(
        string='Fecha elaboración',
        default=fields.Datetime.now,
        readonly=True,
        store=True,
    )

    date_review = fields.Datetime(
        string='Fecha revisado',
        default=fields.Datetime.now,
        readonly=True,
        store=True,
    )

    user_ids = fields.Many2many(
        string='Validado',
        comodel_name='res.users',
        relation='cyber_2matrix_users_rel',
        column1='user_id',
        column2='matrix_id',
    )

    date_validate = fields.Datetime(
        string='Fecha validación',
        readonly=True,
        store=True,
    )

    filter = fields.Selection(
        string='Filtrar por',
        selection=[
            ('none', 'Todos las lineas pendientes'),
            ('date', 'Entre rango de fechas de creación'),
            ('block', 'Por fuentes'),
            ('state', 'Estado de riesgo'),
            ('partial', 'Seleccionar manualmente')],
        default='none',
    )

    date_init = fields.Date(
        string='Fecha inicio',
    )
    date_fin = fields.Date(
        string='Fecha final',
    )

    block_ids = fields.Many2many(
        string='Fuentes',
        comodel_name='cyber_2matrix.block',
        relation='cyber_2matrix_block_line_rel',
        column1='block_id',
        column2='matrix_id',
    )

    state = fields.Selection(
        string='Estado',
        selection=[
            ('elaborate', 'En elaboración'),
            ('review', 'En revisión'),
            ('validate', 'En validación'),
            ('validate_ok', 'Validado'),
            ('cancel', 'Cancelado')],
        default='elaborate',
    )
    state_line = fields.Selection(
        string='Estado',
        selection=[
            ('draft', 'Borrador'),
            ('elaborate', 'En proceso'),
            ('validate', 'Validado'),
            ('cancel', 'Cancelado')],
    )

    line_ids = fields.Many2many(
        string='line',
        comodel_name='cyber_2matrix.block.line',
        relation='cyber_2matrix_m_block_line_rel',
        column1='line_id',
        column2='matrix_id',
    )

    def send_elaborate(self):
        self.state = 'elaborate'

    def send_elaborate_o(self):
        self.exec_filter()
        self.state = 'elaborate'

    '''
    def exec_filter(self):
        type_ = None
        if self.type == 'risk':
            type_ = ('type', '=', 'risk')
        elif self.type == 'oppotunity':
            type_ = ('type', '=', 'opportunity')
        if not filter or not type_:
            return
        if self.filter == 'none':
            self.line_ids = self.env['matrix.block.line'].search(
                [('state', '=', 'elaborate'), type_])
        if self.filter == 'date':
            self.line_ids = self.env['matrix.block.line'].search(
                [('create_date', '<=', self.date_fin), ('create_date', '>=', self.date_init), type_])
        if self.filter == 'block':
            self.line_ids = self.env['matrix.block.line'].search(
                [('block_id', 'in', self.block_ids.ids), type_])
        if self.filter == 'state':
            self.line_ids = self.env['matrix.block.line'].search(
                [('state', '=', self.state_line), type_])
    '''
    def create_action(self, vuser_id):

        action = self.env.ref('hola_calidad.p_mail_activity_action').read()[0]
        self.env.cr.execute("""SELECT id FROM ir_model 
                          WHERE model = %s""", (str(self._name),))
        info = self.env.cr.dictfetchall()
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
                raise exceptions.ValidationError(
                    _('Solo se permite eliminar registros en borrador y en elaboración'))
        return super(Matrix, self).unlink()


class Block(models.Model):
    _name = 'cyber_2matrix.block'
    _description = "Fuente"

    name = fields.Char(
        string='Fuente',
    )

    '''
    type = fields.Selection(
        string='Tipo',
        selection=[
            ('risk', 'Riesgo'),
            ('opportunity', 'Oportunidad')],
    )
    '''
    @api.onchange('process_id')
    def _onchange_process_id(self):
        if self.process_id:
            self.name = self.process_id.process_id.name

    @api.onchange('other')
    def _onchange_other(self):
        self.name = self.other

    process_id = fields.Many2one(
        string='Proceso',
        comodel_name='process.edition',
        ondelete='cascade',
        domain=[('active','=',True)]
    )
    other = fields.Char(
        string='Otro',
    )

    line_ids = fields.One2many(
        string='Lineas',
        comodel_name='cyber_2matrix.block.line',
        inverse_name='block_id',
    )

    state = fields.Selection(
        string='Estado',
        selection=[
            ('draft', 'Borrador'),
            ('elaborate', 'En proceso'),
            ('validate', 'Validado'),
            ('cancel', 'Cancelado')],
        default='draft',
    )

    def send_elaborate(self):
        self.state = 'elaborate'
        for line in self.line_ids:
            line.send_elaborate()

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
    _description = 'Dominio'

    name = fields.Char(string='Nombre')
    description = fields.Text(string='Descripción',)

    ctrl_target_id = fields.One2many(
        string='Objetivos de control',
        comodel_name='cyber_2matrix.block.line.ctrl_target',
        inverse_name='domain_id',
    )

class CyberMatrixBlockLineCtrlTarget(models.Model):
    _name = 'cyber_2matrix.block.line.ctrl_target'
    _description = 'Objetivo de control'

    name = fields.Char(string='Nombre')
    domain_id = fields.Many2one('cyber_2matrix.block.line.domain', string='Dominio')


class Line(models.Model):
    _name = 'cyber_2matrix.block.line'
    _inherit = ['mgmtsystem.version', 'mail.thread',
                'mail.activity.mixin', 'mgmtsystem.code']
    _description = "Declaración de aplicabilidad"

    parent_edition = fields.Many2one(
        comodel_name='cyber_2matrix.block.line', string='Padre', copy=False)
    old_versions = fields.One2many(
        comodel_name='cyber_2matrix.block.line', string='Versiones antiguas',
        inverse_name='parent_edition', context={'active_version': False})

    def action_open_older_versions(self):
        result = self.env.ref(
            'mgmtsystem_opportunity.matrix_block_line_risk_action').read()[0]
        result['domain'] = [('id', 'in', self.old_versions.ids)]
        #result['context'] = {'active_version': False, 'type': self.type}
        return result

    name = fields.Char(
        string='Nombre',
        required=True,
    )
    block_id = fields.Many2one(
        string='Fuente',
        comodel_name='cyber_2matrix.block',
        ondelete='restrict',
    )
    user_id = fields.Many2one(comodel_name='res.users', string='Responsable')

    system_id = fields.Many2one(
        'mgmtsystem.context.system', string='Identificador', default=lambda self: self.env.ref('hola_calidad.policy_system_1'))
    process_id = fields.Many2one('mgmt.categ', string='Proceso')

    description = fields.Text(
        string='Descripción',
    )

    domain_id = fields.Many2one('cyber_2matrix.block.line.domain', string='Dominio')
    domain_description = fields.Text(related='domain_id.description', readonly=True, string='Descripción del Dominio')

    ctrl_target_id = fields.Many2one('cyber_2matrix.block.line.ctrl_target', string='Objetivo de control')


    @api.onchange('domain_id')
    def _onchange_domain_id(self):
        if self.domain_id:
            return {'domain': {'ctrl_target_id': [('domain_id', '=', self.domain_id.id)]}}
        else:
            return {'domain': {'ctrl_target_id': []}}
        
    @api.constrains('ctrl_target_id', 'domain_id')
    def _check_ctrl_target(self):
        if self.ctrl_target_id and self.domain_id and self.ctrl_target_id.domain_id != self.domain_id:
            raise ValidationError(_("El Objetivo de control seleccionado no corresponde al dominio indicado."))


    application = fields.Boolean(string='Aplicación', default=False)
    description_application = fields.Text(string='Descripción de la aplicación',)

    implementation_record = fields.Text(string='Evidencia o registro de implementación',)
    type = fields.Selection(
        string='Tipo',
        selection=[
            ('national', 'Nacional'),
            ('international', 'Internacional')],
    )

    action_ids = fields.Many2many(
        string='Acciones',
        comodel_name='mgmtsystem.action',
        relation='cyber2_block_line_action_rel',
        column1='action_id',
        column2='line_id',
    )

    state = fields.Selection(
        string='Estado',
        selection=[
            ('draft', 'Borrador'),
            ('elaborate', 'En proceso'),
            ('validate', 'Validado'),
            ('cancel', 'Cancelado')],
        default='draft',
    )


    def send_elaborate(self):
        self.state = 'elaborate'

    def send_validate(self):
        self.state = 'validate'

    def send_cancel(self):
        self.state = 'cancel'


    '''important_review_it
    @api.constrains('state')
    def _check_state(self):
        for record in self:
            if record.type == 'opportunity':
                if record.state == 'validate' and record.ntr >= 8 and not record.action_ids:
                    raise exceptions.ValidationError(
                        _('Valor de oportunidad muy alto. Para validar tiene que ingresar al menos una acción'))
            if record.type == 'risk':
                if record.state == 'validate' and record.ntr >= 100 and not record.action_ids:
                    raise exceptions.ValidationError(
                        _('Valor de riesgo muy alto. Para validar tiene que ingresar al menos una acción'))
    '''