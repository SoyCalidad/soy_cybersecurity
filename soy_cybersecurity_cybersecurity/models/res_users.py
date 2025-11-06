from odoo import models, fields 


class ResUsers(models.Model):
    _inherit = "res.users"
    
    scc_report_incident = fields.Boolean(string="Recibir notificación del incidente", default=False,)