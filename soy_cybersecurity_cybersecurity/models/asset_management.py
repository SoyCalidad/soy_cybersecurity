# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError


_ASSET_INTERPRETATION = 'El valor del activo de la información permite evaluar los diferentes niveles y ordenarlos según sus prioridades. Cuando se obtengan Números de Prioridad de Activos elevados (mayores a 100) se establecerán acciones.'
_OPP_INTERPRETATION = 'El valor de oportunidad permite evaluar los diferentes niveles de oportunidades y ordenarlas según sus prioridades. Cuando se obtengan Números de Prioridad de Oportunidad elevados (Entre 8-10) se debe establecer acciones inmediatas para aprovechar la oportunidad, índices más bajos a estos deben ser evaluados cuidadosamente en cuanto a costo y beneficio.'


class Categ(models.Model):
    _name = 'cyber_matrix.categ'
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
    '''
    type = fields.Selection(
        string='Tipo',
        selection=[
            ('risk', 'Riesgo'),
            ('opportunity', 'Oportunidad')],
    )
    '''
    matrix_ids = fields.One2many(
        string='Matrices',
        comodel_name='cyber_matrix.matrix',
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
    _name = 'cyber_matrix.matrix'
    _inherit = ['mgmtsystem.validation.mail', 'mgmtsystem.code']
    _description = "Matriz"

    parent_edition = fields.Many2one(
        comodel_name='cyber_matrix.matrix', string='Padre', copy=False)
    old_versions = fields.One2many(
        comodel_name='cyber_matrix.matrix', string='Versiones antiguas',
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
        comodel_name='cyber_matrix.categ',
        ondelete='cascade',
    )
    system_id = fields.Many2one(
        'mgmtsystem.context.system', string='Identificador de riesgo', default=lambda self: self.env.ref('hola_calidad.policy_system_1'))
    actions_count = fields.Integer(
        string='Acciones',
    )
    nonconformities_count = fields.Integer(
        string='No conformidades',
    )
    indicators_count = fields.Integer(
        string='Indicadores',
    )
    targets_count = fields.Integer(
        string='Objetivos',
    )
    change_requests_count = fields.Integer(
        string='Solicitudes de cambios',
    )
    # risks_count = fields.Integer(
    #     string='Riesgos',
    # )
    # opps_count = fields.Integer(
    #     string='Oportunidades',
    # )

    @api.onchange('categ_id')
    def _onchange_categ_id(self):
        if self.categ_id:
            self.name = self.categ_id.name + " " + self.numero

    type = fields.Selection(
        string='Tipo',
        selection=[
            ('risk', 'Riesgo'),
            ('opportunity', 'Oportunidad')],
        required=False,
    )
    '''
    type = fields.Selection(
        string='Tipo',
        selection=[
            ('risk', 'Riesgo'),
            ('opportunity', 'Oportunidad')],
        required=True,
    )
    
    @api.onchange('type')
    def _onchange_type(self):
        return {
            'domain': {
                'categ_id': [('type', '=', self.type)]
            }
        }
    '''

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
        relation='cyber_matrix_users_rel',
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
        comodel_name='cyber_matrix.block',
        relation='cyber_matrix_block_line_rel',
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
        comodel_name='cyber_matrix.block.line',
        relation='cyber_matrix_m_block_line_rel',
        column1='line_id',
        column2='matrix_id',
    )
    risk_ids = fields.Many2many('matrix.block.line',
                                relation='cyber_matrix_matrix_risk_rel',
                                column1='risk_id',
                                column2='cyber_matrix_matrix_id',
                                string='Riesgos',
                                domain=[('type', '=', 'risk')])
    risks_count = fields.Integer(compute='_compute_risks_count', string='Riesgos')

    opp_ids = fields.Many2many('matrix.block.line',
                               relation='cyber_matrix_matrix_opp_rel',
                               column1='opp_id',
                               column2='cyber_matrix_matrix_id',
                               string='Oportunidades',
                               domain=[('type', '=', 'opportunity')])
    opps_count = fields.Integer(compute='_compute_opps_count', string='Oportunidades')

    @api.depends('risk_ids')
    def _compute_risks_count(self):
        for each in self:
            each.risks_count = 0
            if each.risk_ids:
                each.risks_count = len(each.risk_ids)

    @api.depends('opp_ids')
    def _compute_opps_count(self):
        for each in self:
            each.opps_count = 0
            if each.opp_ids:
                each.opps_count = len(each.opp_ids)

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
    _name = 'cyber_matrix.block'
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
        comodel_name='cyber_matrix.block.line',
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


class LineAgent(models.Model):
    _name = 'cyber_matrix.block.line.agent'
    _description = 'Agente Riesgo/Oportunidad'

    name = fields.Char(string='Nombre')
    description = fields.Text(string='Descripción')

'''
class LineType(models.Model):
    _name = 'cyber_matrix.block.line.type'
    _description = 'Tipo Riesgo/Oportunidad'

    name = fields.Char(string='Nombre')
    description = fields.Text(string='Descripción')
'''

class MatrixBlockLineSystem(models.Model):
    _name = 'cyber_matrix.block.line.system'
    _description = 'Identificador de riesgo'

    name = fields.Char(string='Nombre')


class MatrixBlockLineSystem(models.Model):
    _name = 'cyber_matrix.block.line.resource'
    _description = 'Recurso de activos de información'

    name = fields.Char(string='Recurso')

class MatrixBlockLineSystem(models.Model):
    _name = 'cyber_matrix.block.line.location'
    _description = 'Ubicación de activos de información'

    name = fields.Char(string='Ubicación')

class MatrixBlockLineSystem(models.Model):
    _name = 'cyber_matrix.block.line.language'
    _description = 'Idioma de activos de información'

    name = fields.Char(string='Idioma')

class MatrixBlockLineSystem(models.Model):
    _name = 'cyber_matrix.block.line.asset_type'
    _description = 'Tipos de activos de información'

    name = fields.Char(string='Tipos de activo')


class Line(models.Model):
    _name = 'cyber_matrix.block.line'
    _inherit = ['mgmtsystem.version', 'mail.thread',
                'mail.activity.mixin', 'mgmtsystem.code']
    _description = "Inventario de activos de información"

    parent_edition = fields.Many2one(
        comodel_name='cyber_matrix.block.line', string='Padre', copy=False)
    old_versions = fields.One2many(
        comodel_name='cyber_matrix.block.line', string='Versiones antiguas',
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
        comodel_name='cyber_matrix.block',
        ondelete='restrict',
    )
    user_id = fields.Many2one(comodel_name='res.users', string='Responsable')

    agent_id = fields.Many2one(
        comodel_name='cyber_matrix.block.line.agent', string='Agente de la causa')
    '''
    type_id = fields.Many2one(
        comodel_name='cyber_matrix.block.line.type', string='Tipo')
    '''
    system_id = fields.Many2one(
        'mgmtsystem.context.system', string='Identificador', default=lambda self: self.env.ref('hola_calidad.policy_system_1'))
    process_id = fields.Many2one('mgmt.categ', string='Proceso')

    '''
    def _get_interpretation(self):
        if self.type == 'risk':
            self.interpretation = 'El valor de riesgo permite evaluar los diferentes niveles de riesgo y ordenarlos según sus prioridades. Cuando se obtengan Números de Prioridad de Riesgo elevados (mayores a 100) se establecerán acciones de mejora para reducirlos'
        elif self.type == 'opportunity':
            self.interpretation = 'El valor de oportunidad permite evaluar los diferentes niveles de oportunidades y ordenarlas según sus prioridades. Cuando se obtengan Números de Prioridad de Oportunidad elevados (Entre 8-10) se debe establecer acciones inmediatas para aprovechar la oportunidad, índices más bajos a estos deben ser evaluados cuidadosamente en cuanto a costo y beneficio.'
        else:
            self.interpretation = 'a'
    '''
    interpretation_asset = fields.Text(
        string='Interpretación', default=_ASSET_INTERPRETATION)
    interpretation_opportunity = fields.Text(
        string='Interpretación', default=_OPP_INTERPRETATION)

    '''
    @api.onchange('block_id')
    def _onchange_block_id(self):
        if not self.block_id:
            return
        self.type = self.block_id.type

    type = fields.Selection(
        string='Tipo',
        selection=[
            ('risk', 'Riesgo'),
            ('opportunity', 'Oportunidad')],
        required=True,
    )

    @api.onchange('type')
    def _onchange_type(self):
        return {
            'domain': {
                'evaluation_id': [('type', '=', self.type)]
            }
        }
    '''

    asset_contains_personal_data = fields.Boolean(string='El activo contiene datos personales', default=False)
    asset_susceptible_to_fraud = fields.Boolean(string='El activo es susceptible de fraude o corrupción', default=False)
    asset_vital_for_organization = fields.Boolean(string='El activo es vital para la operación de la organización', default=False)

    resource_id = fields.Many2many('cyber_matrix.block.line.resource', string='Recurso')

    location_id = fields.Many2many('cyber_matrix.block.line.location', string='Ubicación')

    language_id = fields.Many2many('cyber_matrix.block.line.language', string='Idioma')

    asset_type_id = fields.Many2many('cyber_matrix.block.line.asset_type', string='Tipo')

    storage_medium = fields.Selection(
        string='Medio de Conservación',
        selection=[
            ('physical', 'Física'),
            ('digital', 'Digital')],
    )

    department_id = fields.Many2one(
        string='Area',
        comodel_name='hr.department',
    )
    description = fields.Text(
        string='Descripción',
    )

    #
    effect = fields.Text(
        string='Efecto',
    )
    cause = fields.Text(
        string='Causa',
    )
    #

    evaluation_id = fields.Many2one(
        string='Evaluación',
        comodel_name='cyber_evaluation.evaluation',
        ondelete='restrict',
    )
    result_ids = fields.Many2many(
        string='Resultados',
        comodel_name='cyber_evaluation.result',
        relation='cyber_block_line_evaluation_result_rel',
        column1='result_id',
        column2='line_id',
        copy=True,
    )
    ntr = fields.Integer(
        string='Valor del Activo',
    )
    action_ids = fields.Many2many(
        string='Acciones',
        comodel_name='mgmtsystem.action',
        relation='cyber_block_line_action_rel',
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
    risk_ids = fields.Many2many('matrix.block.line',
                                relation='cyber_matrix_block_line_risk_rel',
                                column1='risk_id',
                                column2='cyber_matrix_block_line_id',
                                string='Riesgos',
                                domain=[('type', '=', 'risk')])
    risks_count = fields.Integer(compute='_compute_risks_count', string='Riesgos')

    opp_ids = fields.Many2many('matrix.block.line',
                               relation='cyber_matrix_block_line_opp_rel',
                               column1='opp_id',
                               column2='cyber_matrix_block_line_id',
                               string='Oportunidades',
                               domain=[('type', '=', 'opportunity')])
    opps_count = fields.Integer(compute='_compute_opps_count', string='Oportunidades')

    @api.depends('risk_ids')
    def _compute_risks_count(self):
        for each in self:
            each.risks_count = 0
            if each.risk_ids:
                each.risks_count = len(each.risk_ids)

    @api.depends('opp_ids')
    def _compute_opps_count(self):
        for each in self:
            each.opps_count = 0
            if each.opp_ids:
                each.opps_count = len(each.opp_ids)

    def write(self, vals):
        res = super().write(vals)
        print([x.criterio_id.name for x in self.result_ids])
        return res

    def send_elaborate(self):
        self.state = 'elaborate'

    def send_validate(self):
        self.state = 'validate'

    def send_cancel(self):
        self.state = 'cancel'

    def create_criterio(self):
        lines = [(5, 0, 0)]
        for criterio in self.evaluation_id.criterio_ids:
            data = {
                'criterio_id': criterio,
                'name': criterio.name,
                'description': criterio.description,
            }
            lines.append((0, 0, data))
        return lines

    @api.onchange('evaluation_id')
    def _onchange_evaluation_id(self):
        lines = self.create_criterio()
        self.result_ids = lines

    @api.onchange('result_ids')
    def _onchange_result_ids(self):
        ntr_tmp = 1
        for result in self.result_ids:
            ntr_tmp *= result.value
        self.ntr = ntr_tmp

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