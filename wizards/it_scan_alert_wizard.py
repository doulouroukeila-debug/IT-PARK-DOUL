from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ItScanAlertWizard(models.TransientModel):
    _name = 'it.scan.alert.wizard'
    _description = 'Assistant de scan des alertes'

    days_ahead = fields.Integer(string='Jours avant échéance', required=True, default=30)
    result = fields.Text(string='Résultat', readonly=True)
    state = fields.Selection([
        ('choose', 'Paramètres'),
        ('result', 'Résultat'),
    ], string='État', default='choose')

    def action_scan(self):
        self.ensure_one()
        Alert = self.env['it.alert']
        created = Alert.scan_alerts(self.days_ahead)
        self.write({
            'state': 'result',
            'result': _('Scan terminé.\nAlertes créées : %d\nPériode : %d jours') % (created, self.days_ahead),
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'it.scan.alert.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
