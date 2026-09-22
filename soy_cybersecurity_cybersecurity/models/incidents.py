from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class incidentCateg(models.Model):
    _name = 'incident.categ'
    _order = 'sequence asc'

    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company,
    )
    elaborate_ids = fields.Many2one(
        string=u'Opened by',
        comodel_name='res.users',
        default=lambda self: self.env.user
    )

    name = fields.Char(
        string='Name',
        required=True,
    )
    sequence = fields.Integer(
        string='Priority',
        default=5,
    )
    description = fields.Text(
        string='Description',
    )


class incidentVia(models.Model):
    _name = 'incident.via'
    _description = 'Claim Method'

    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company,
    )
    elaborate_ids = fields.Many2one(
        string=u'Prepared by',
        comodel_name='res.users',
        default=lambda self: self.env.user
    )
    name = fields.Char(
        string='Name',
        required=True,
    )
    description = fields.Text(
        string='Description',
    )


class incidentQuickAction(models.Model):
    _name = 'incident.quick.action'
    _order = 'sequence asc'
    _description = 'Quick action for claim'

    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company,
    )
    elaborate_ids = fields.Many2one(
        string=u'Prepared by',
        comodel_name='res.users',
        default=lambda self: self.env.user
    )

    name = fields.Char(
        string='Action',
        required=True,
    )
    categ_id = fields.Many2one(
        string='Category',
        comodel_name='incident.categ',
    )
    sequence = fields.Integer(
        string='Priority',
        default=5,
    )
    description = fields.Text(
        string='Description',
    )


class incidentReason(models.Model):
    _name = 'incident.incident.reason'
    _description = 'Reason'

    name = fields.Text(string='Name')
    description = fields.Text(string='Description')


class incidentincidentCauseWhy(models.Model):
    _inherit = 'mgmtsystem.nonconformity.cause_why'

    # One2many references

    incident_cause_id = fields.Many2one(
        'incident.incident', string='Claim (Cause)', ondelete='set null')
    incident_why_id = fields.Many2one(
        'incident.incident', string='Claim (Why?)', ondelete='set null')

class incident(models.Model):
    _name = 'incident.incident'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mgmtsystem.code']
    _order = 'date_incident desc'
    _description = 'Claim'

    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company,
    )
    elaborate_ids = fields.Many2one(
        string=u'Prepared by',
        comodel_name='res.users',
        default=lambda self: self.env.user
    )
    name = fields.Char(
        string='Name',
        required=True,
    )
    description = fields.Text(
        string='Company Perspective',
    )
    perspective = fields.Text(
        string='Notifier Description',
    )
    date_incident = fields.Datetime(
        string='Detection Date',
        default=fields.Datetime.now,
        required=True,
    )
    date_fin = fields.Datetime(
        string='Completion Date',
    )
    validation_date = fields.Date('Validation Date')
    reason_ids = fields.Many2many(
        'incident.incident.reason', string='Reason')
    reason_other = fields.Text('Other Reason')

    
    analisis_id = fields.Many2one(
        string='Analysis',
        comodel_name='incident.analisis',
        ondelete='restrict',
    )

    
    categ_id = fields.Many2one(
        string='Category',
        comodel_name='incident.categ',
    )
    
    department_id = fields.Many2one(
        string='Involved Area',
        comodel_name='hr.department',
    )
    partner_id = fields.Many2one(
        string='Notifying Customer',
        comodel_name='res.partner',
    )
    via_ids = fields.Many2many(
        string='Method',
        comodel_name='incident.via',
        relation='incident_via_rel',
        column1='via_id',
        column2='incident_id',
    )
    quick_action_id = fields.Many2one(
        string='Quick Action',
        comodel_name='incident.quick.action',
    )
    quick_response = fields.Text(
        string='Notifier Response',
    )
    is_open = fields.Boolean(
        string='Opening of Corrective Action',
        help="If the affected party does not accept the quick action, non-conformities and actions are opened",
        default=False,
    )
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    date_solution = fields.Datetime(
        string='Solution Date',
    )
    action_ids = fields.Many2many(
        string='Action',
        comodel_name='mgmtsystem.action',
        relation='action_incident_rel',
        column1='action_id',
        column2='incident_id',
    )
    nonconformity_ids = fields.Many2many(
        string=u'Non-conformities',
        comodel_name='mgmtsystem.nonconformity',
        relation='nonconformity_incident_rel',
        column1='nonconformity_id',
        column2='incident_id',
    )

    state = fields.Selection(
        string='Status',
        selection=[
            ('open', 'Open'),
            ('in_process', 'In Process'),
            ('close', 'Closed'),
            ('cancel', 'Cancelled')],
        default='open',
    )
    # Tipos en realidad son: Interna o externa, no se pudo cambiar el selection por todo lo avanzado
    type = fields.Selection(
        string='Type',
        selection=[
            ('internal', 'Internal'),
            ('ext', 'External')],
    )
    type_partner = fields.Selection(
        string='Partner Type',
        selection=[
            ('internal', 'Customer'),
            ('ext', 'Vendor')],
    )

    investigation = fields.Text(string='Investigation')
    conclusions = fields.Text(string='Conclusions')

    investigation_method = fields.Selection([
        ('cause', 'Cause-and-Effect Analysis'),
        ('why', '5 Whys'),
    ], string='Investigation Method')

    cause_ids = fields.One2many(
        'mgmtsystem.nonconformity.cause_why', 'incident_cause_id', string='Causes')

    why_ids = fields.One2many(
        'mgmtsystem.nonconformity.cause_why', 'incident_why_id', string='Whys')

    root_cause = fields.Char(string='Root Cause')

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
        string='Response to Action',
    )
    satisfied = fields.Boolean(
        string='Satisfied',
    )

    product_id = fields.Many2one(
        string='Product/Service',
        comodel_name='product.product',
    )
    reclamation_book = fields.Boolean(
        string='Was the Complaints Book filled out?')
    employee_id = fields.Many2one('hr.employee', string='Handled by')
    employee_notify_id = fields.Many2one(
        'hr.employee', string='Notified by')
    place = fields.Char(string='Location where the incident occurred')
    responsable_id = fields.Many2one('res.users', 'Responsible')

    incident_files = fields.Binary(string='Attachments', attachment=True)

    # Contact data

    complainer_name = fields.Char(string='Full Name')
    complainer_phone = fields.Char(string='Phone')
    complainer_email = fields.Char(string='Email')

    complainer_document_type = fields.Selection([
        ('dni', 'ID Card (DNI)'),
        ('car', 'Foreign ID'),
        ('pas', 'Passport'),
    ], string='Document Type')

    complainer_document_number = fields.Char(string='Document Number')

    complainer_delivery_type = fields.Selection([
        ('email', 'I want to receive it by email'),
        ('phone', 'I want to receive it by mobile phone'),
    ], string='Communication Method')

    @api.onchange('satisfied')
    def _onchange_satisfied(self):
        if self.satisfied:
            self.state = 'close'

    @api.onchange('quick_action_id')
    def onchange_quick_action_id(self):
        if self.quick_action_id:
            if not self.investigation:
                raise UserError('The investigation field is empty')
            if not self.investigation_method=='why' and not self.conclusions:
                raise UserError('The conclusions field is empty')
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
