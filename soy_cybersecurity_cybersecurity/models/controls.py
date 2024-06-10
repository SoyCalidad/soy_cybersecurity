from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class Line(models.Model):
    _inherit = 'cyber_2matrix.block.line'
    #_description = "Controles"

    type_ctrl = fields.Selection(
        string='Tipo de control',
        selection=[
            ('app_ctrl', 'Declaración de Aplicabilidad'),
            ('controls', 'Controles')]   
    )


    executor_user_id = fields.Many2one('res.users', string='Responsable de Ejecución')
    tracking_hr_employee_id = fields.Many2one('hr.employee', string='Responsable de Seguimiento')
    authorizing_user_id = fields.Many2one('res.users', string='Autoridad Aprobatoria')

    opening_date = fields.Datetime(
        string='Fecha de Apertura',
        default=fields.Datetime.now,
        store=True,
    )

    periodic_control = fields.Boolean(string='Control Periódico', default=False)

    deadline = fields.Datetime(
        string='Fecha límite',
        store=True,
    )

    reference = fields.Text(
        string='Referencia',
    )

    priority = fields.Selection(
        string='Prioridad',
        selection=[
            ('0', 'No establecida'),
            ('1', 'Baja'),
            ('2', 'Media'),
            ('3', 'Alta')],
        default='0',
    )

    def button_custom_save_redirect(self):
        self.ensure_one()
        # Actualiza el registro y cambia el campo type_ctrl
        self.write({'type_ctrl': 'app_ctrl'})
        # Redirige al usuario a otra vista formulario para continuar la edición
        view_id = self.env.ref('soy_cybersecurity_cybersecurity.cyber_view_2matrix_block_line_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Editar Campos Adicionales',
            'view_mode': 'form',
            'res_model': 'cyber_2matrix.block.line',
            'res_id': self.id,
            'view_id': view_id,
            'target': 'current',
            'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
        }