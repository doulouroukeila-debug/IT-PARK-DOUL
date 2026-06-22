from odoo import models, fields, api, _


class ItAlertScanWizard(models.TransientModel):
    _name = 'it.alert.scan.wizard'
    _description = 'Assistant de scan des alertes'

    alert_count = fields.Integer(string='Alertes générées', readonly=True)
    state = fields.Selection([
        ('start', 'Démarrer'),
        ('result', 'Résultat'),
    ], string='État', default='start')

    def action_scan(self):
        self.env['it.alert'].scan_alerts()
        alert_count = self.env['it.alert'].search_count([
            ('state', '=', 'pending'),
        ])
        self.write({
            'alert_count': alert_count,
            'state': 'result',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'it.alert.scan.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}
