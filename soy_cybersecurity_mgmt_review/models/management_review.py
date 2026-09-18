# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError

XMLID_ACTION_SOA_MATRIX = "soy_cybersecurity_cybersecurity.matrix_matrix_app_ctrl_mgmt_action"


class ManagementReview(models.Model):
    _inherit = 'management.review'


    it_security_target = fields.Html( 
        string='Objetivo de seguridad de la información',
        store=True,)
    
    it_security_target_description = fields.Text( string='Interpretación')

    it_legal_requirements = fields.Html( 
        string='Requerimientos legales y otros requerimientos',
        store=True,)
    
    it_legal_requirements_description = fields.Text( string='Interpretación')

    # G. COMUNICACIONES PERTINENTES CON LAS PARTES INTERESADAS

    # it_comunication_plan_ids = fields.Many2many(
    #     'comunication.plan.line', string='Planes de Comunicación')
    it_comunication_plan_ids = fields.Many2many(
        'comunication.plan.line',
        relation='management_review_it_comunication_plan_rel',
        string='Planes de Comunicación')
    it_comunication_plan = fields.Html('Comunicaciones')
    it_comunication_plan_interpretation = fields.Text(
        'Interpretación de las comunicaciones')
    
    type_review = fields.Selection(
        selection_add=[
            ('iso27k', '27001'),
        ],
    )
    
    sc27k_soa_matrix_html = fields.Html(string="Matriz de riesgos / plan de tratamiento / SoA")
    sc27k_soa_matrix_inter = fields.Text(string="Interpretacion: Matriz de riesgos / plan de tratamiento / SoA")
    
    def generate_soa_matrix_html(self):
        if self.is_last:
            matrix_ids = self.env['cyber_2matrix.matrix'].search([], order="create_date desc", limit=1)
        else:
            matrix_ids = self.env['cyber_2matrix.matrix'].search([
                ('date_validate', '>=', self.date_ini), 
                ('date_validate', '<=', self.date_fin)
            ], order="create_date desc")
        data_tmp = "<table class='table table-bordered'>"
        data_tmp += "<tr><td><strong>Dominio</strong></td><td><strong>Nombre</strong></td><td><strong>Descripción del control</strong></td><td><strong>Aplicabilidad</strong></td><td><strong>Justificación</strong></td></tr>"
        application_dict = dict(self.env['cyber_2matrix.matrix.line']._fields['application'].selection)
        action = self.env.ref(XMLID_ACTION_SOA_MATRIX, raise_if_not_found=False)
        for data in matrix_ids:
            
            for line in data.line_ids:
                link = (
                    '<a href="/odoo/action-%s/%s" '
                    'data-oe-id="%s" '
                    'data-oe-model="cyber_2matrix.matrix">%s</a>'
                ) % (
                    action.id if action else 0,
                    data.id,
                    data.id,
                    line.applicability_id_name or 'Sin nombre',
                )
                data_tmp += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
                line.applicability_id_domain_id.display_name or '', link, line.applicability_id_description_application or '', application_dict.get(line.application, ''), line.justification or '')
        data_tmp = data_tmp + "</table>"
        return data_tmp

    def update_data(self):
        super().update_data()
        
        if self.type_review == 'iso27k':
            self.generate_record_meeting_ids()
            self.foda = self.generate_foda()
            self.generate_stakeholders()
            self.nonconformity_action = self.generate_nonconformity_action()
            self.target = self.generate_target()
            self.audit = self.generate_audit_plan_html()
            self.measurement_html = self.generate_target()
            self.communication_plan_html = self.generate_comunication_program_html()
            self.sc27k_soa_matrix_html = self.generate_soa_matrix_html()
            self.improve_action = self.generate_improve_action()
            

    
