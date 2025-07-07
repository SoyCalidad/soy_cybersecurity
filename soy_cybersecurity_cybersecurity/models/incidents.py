from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class incidentCateg(models.Model):
    _name = 'incident.categ'
    _order = 'sequence asc'

    elaborate_ids = fields.Many2one(
        string=u'Abierto por',
        comodel_name='res.users',
        default=lambda self: self.env.user
    )

    name = fields.Char(
        string='Nombre',
        required=True,
    )
    sequence = fields.Integer(
        string='Prioridad',
        default=5,
    )
    description = fields.Text(
        string='Descripción',
    )


class incidentVia(models.Model):
    _name = 'incident.via'
    _description = 'Vía de reclamo'

    elaborate_ids = fields.Many2one(
        string=u'Elaborado',
        comodel_name='res.users',
        default=lambda self: self.env.user
    )
    name = fields.Char(
        string='Nombre',
        required=True,
    )
    description = fields.Text(
        string='Descripción',
    )


class incidentQuickAction(models.Model):
    _name = 'incident.quick.action'
    _order = 'sequence asc'
    _description = 'Acción rápida para reclamo'

    elaborate_ids = fields.Many2one(
        string=u'Elaborado por',
        comodel_name='res.users',
        default=lambda self: self.env.user
    )

    name = fields.Char(
        string='Acción',
        required=True,
    )
    categ_id = fields.Many2one(
        string='Categoría',
        comodel_name='incident.categ',
    )
    sequence = fields.Integer(
        string='Prioridad',
        default=5,
    )
    description = fields.Text(
        string='Descripción',
    )


class incidentReason(models.Model):
    _name = 'incident.incident.reason'
    _description = 'Motivo'

    name = fields.Text(string='Nombre')
    description = fields.Text(string='Descripción')


class incidentincidentCauseWhy(models.Model):
    _inherit = 'mgmtsystem.nonconformity.cause_why'

    # One2many references

    incident_cause_id = fields.Many2one(
        'incident.incident', string='Reclamo (Causa)', ondelete='set null')
    incident_why_id = fields.Many2one(
        'incident.incident', string='Reclamo (¿Por qué?)', ondelete='set null')

class incident(models.Model):
    _name = 'incident.incident'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mgmtsystem.code']
    _order = 'date_incident desc'
    _description = 'Reclamo'

    elaborate_ids = fields.Many2one(
        string=u'Elaborado',
        comodel_name='res.users',
        default=lambda self: self.env.user
    )
    name = fields.Char(
        string='Nombre',
        required=True,
    )
    description = fields.Text(
        string='Perspectiva de la empresa',
    )
    perspective = fields.Text(
        string='Descripción del notificante',
    )
    date_incident = fields.Datetime(
        string='Fecha detección',
        default=fields.Datetime.now,
        required=True,
    )
    date_fin = fields.Datetime(
        string='Fecha finalización',
    )
    validation_date = fields.Date('Fecha de validación')
    reason_ids = fields.Many2many(
        'incident.incident.reason', string='Motivo')
    reason_other = fields.Text('Otro motivo')

    
    analisis_id = fields.Many2one(
        string='Analisis',
        comodel_name='incident.analisis',
        ondelete='restrict',
    )

    
    categ_id = fields.Many2one(
        string='Categoría',
        comodel_name='incident.categ',
    )
    
    department_id = fields.Many2one(
        string='Área implicada',
        comodel_name='hr.department',
    )
    partner_id = fields.Many2one(
        string='Cliente que notifica',
        comodel_name='res.partner',
    )
    via_ids = fields.Many2many(
        string='Medio',
        comodel_name='incident.via',
        relation='incident_via_rel',
        column1='via_id',
        column2='incident_id',
    )
    quick_action_id = fields.Many2one(
        string='Acción rápida',
        comodel_name='incident.quick.action',
    )
    quick_response = fields.Text(
        string='Respuesta del notificante',
    )
    is_open = fields.Boolean(
        string='Apertura de acción correctiva',
        help="Si el afectado no acepta la acción rápida se realiza la apertura de No conformidades y acciones",
        default=False,
    )
    attachment_ids = fields.Many2many('ir.attachment', string='Adjuntos')
    date_solution = fields.Datetime(
        string='Fecha de solución',
    )
    action_ids = fields.Many2many(
        string='Acción',
        comodel_name='mgmtsystem.action',
        relation='action_incident_rel',
        column1='action_id',
        column2='incident_id',
    )
    nonconformity_ids = fields.Many2many(
        string=u'No conformidades',
        comodel_name='mgmtsystem.nonconformity',
        relation='nonconformity_incident_rel',
        column1='nonconformity_id',
        column2='incident_id',
    )

    state = fields.Selection(
        string='Estado',
        selection=[
            ('open', 'Abierto'),
            ('in_process', 'En proceso'),
            ('close', 'Cerrado'),
            ('cancel', 'Cancelado')],
        default='open',
    )
    # Tipos en realidad son: Interna o externa, no se pudo cambiar el selection por todo lo avanzado
    type = fields.Selection(
        string='Tipo',
        selection=[
            ('internal', 'Interna'),
            ('ext', 'Externa')],
    )
    type_partner = fields.Selection(
        string='Tipo de socio',
        selection=[
            ('internal', 'Cliente'),
            ('ext', 'Proveedor')],
    )

    investigation = fields.Text(string='Investigación')
    conclusions = fields.Text(string='Conclusiones')

    investigation_method = fields.Selection([
        ('cause', 'Análisis causa-efecto'),
        ('why', '5 ¿Por qué?'),
    ], string='Metodo de investigación')

    cause_ids = fields.One2many(
        'mgmtsystem.nonconformity.cause_why', 'incident_cause_id', string='Causas')

    why_ids = fields.One2many(
        'mgmtsystem.nonconformity.cause_why', 'incident_why_id', string='¿Por qué?')

    root_cause = fields.Char(string='Causa raiz')

    @api.onchange('type_partner')
    def _onchange_type_partner(self):
        if not self.type_partner:
            return
        if self.type_partner == 'internal':
            return {'domain': {
                    'partner_id': [('customer', '=', True)]
                    }}
        elif self.type_partner == 'ext':
            return {'domain': {
                    'partner_id': [('supplier', '=', True)]
                    }}

    response = fields.Text(
        string='Respuesta ante la acción',
    )
    satisfied = fields.Boolean(
        string='Satisfecho',
    )

    product_id = fields.Many2one(
        string='Producto/Servicio',
        comodel_name='product.product',
    )
    reclamation_book = fields.Boolean(
        string='¿Se llenó el libro de reclamaciones?')
    employee_id = fields.Many2one('hr.employee', string='Atendida por')
    employee_notify_id = fields.Many2one(
        'hr.employee', string='Notificada por')
    place = fields.Char(string='Lugar donde ocurrió el incidente')
    responsable_id = fields.Many2one('res.users', 'Responsable')

    incident_files = fields.Binary(string='Anexos', attachment=True)

    # Contact data

    complainer_name = fields.Char(string='Nombres y apellidos')
    complainer_phone = fields.Char(string='Teléfono')
    complainer_email = fields.Char(string='Correo electrónico')

    complainer_document_type = fields.Selection([
        ('dni', 'DNI'),
        ('car', 'Carnet de extranjería'),
        ('pas', 'Pasaporte'),
    ], string='Tipo de documento')

    complainer_document_number = fields.Char(string='Numero de documento')

    complainer_delivery_type = fields.Selection([
        ('email', 'Quiero recibirla por correo electronico'),
        ('phone', 'Quiero recibirla por celular'),
    ], string='Medio de comunicación')

    @api.onchange('satisfied')
    def _onchange_satisfied(self):
        if self.satisfied:
            self.state = 'close'

    @api.onchange('quick_action_id')
    def onchange_quick_action_id(self):
        if self.quick_action_id:
            if not self.investigation:
                raise UserError('El campo de investigación está vacio')
            if not self.conclusions:
                raise UserError('El campo de conclusiones está vacio')
        if self.quick_action_id:
            self.state = 'in_process'

    @api.onchange('is_open')
    def onchange_is_open(self):
        if self.is_open:
            self.state = 'in_process'


    @api.onchange('categ_id')
    def _onchange_categ_id(self):
        if not self.categ_id:
            return
        return {'domain': {
            'quick_action_id': [('categ_id', 'in', (self.categ_id.id, False))]
        }}

    @api.onchange('state')
    def _onchange_state(self):
        if self.state == 'close':
            self.date_fin = fields.Datetime.now(self)
        else:
            self.date_fin = False

    @api.onchange('nonconformity_ids')
    def _onchange_nonconformity_ids(self):
        self.action_ids = self.env['mgmtsystem.action'].search(
            [('nonconformity_ids', 'in', self.nonconformity_ids.ids)])
