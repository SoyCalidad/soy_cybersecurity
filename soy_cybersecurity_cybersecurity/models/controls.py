from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class Line(models.Model):
    _inherit = 'cyber_2matrix.block.line'
    #_description = "Controles"

    type_ctrl = fields.Selection(
        string='Control Type',
        selection=[
            ('app_ctrl', 'Statement of Applicability'),
            ('controls', 'Controls')]   
    )

    executor_user_id = fields.Many2one('res.users', string='Execution Person Responsible', ondelete='set null')
    tracking_hr_employee_id = fields.Many2one('hr.employee', string='Tracking Person Responsible', ondelete='set null')
    authorizing_user_id = fields.Many2one('res.users', string='Approving Authority', ondelete='set null')

    opening_date = fields.Datetime(
        string='Opening Date',
        default=fields.Datetime.now,
        store=True,
    )

    periodic_control = fields.Boolean(string='Periodic Control', default=False)

    deadline = fields.Datetime(
        string='Deadline',
        store=True,
    )

    reference = fields.Text(
        string='Reference',
    )

    priority = fields.Selection(
        string='Priority',
        selection=[
            ('0', 'Not Set'),
            ('1', 'Low'),
            ('2', 'Medium'),
            ('3', 'High')],
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
            'name': 'Edit Additional Fields',
            'view_mode': 'form',
            'res_model': 'cyber_2matrix.block.line',
            'res_id': self.id,
            'view_id': view_id,
            'target': 'current',
            'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
        }