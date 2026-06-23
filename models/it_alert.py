from odoo import models, fields, api, _
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class ItAlert(models.Model):
    _name = 'it.alert'
    _description = 'Alerte'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'alert_date desc, id desc'

    name = fields.Char(string='Titre', required=True, tracking=True)
    alert_type = fields.Selection([
        ('warranty', 'Expiration de garantie'),
        ('contract', 'Expiration de contrat'),
    ], string='Type', required=True, tracking=True)

    equipment_id = fields.Many2one('it.equipment', string='Équipement', tracking=True)
    contract_id = fields.Many2one('it.contract', string='Contrat', tracking=True)
    old_date = fields.Date(string='Date d\'échéance', tracking=True)

    alert_date = fields.Date(string="Date de l'alerte", required=True, default=fields.Date.today, tracking=True)
    days_before_expiry = fields.Integer(string='Jours avant expiration', tracking=True)
    is_read = fields.Boolean(string='Lu', default=False)
    is_resolved = fields.Boolean(string='Résolu', default=False)

    state = fields.Selection([
        ('pending', 'En attente'),
        ('resolved', 'Résolu'),
    ], string='Statut', default='pending', tracking=True)

    user_id = fields.Many2one('res.users', string='Assigné à', default=lambda self: self.env.user)

    def action_resolve(self):
        self.write({'state': 'resolved', 'is_resolved': True})

    def action_mark_read(self):
        self.write({'is_read': True})

    @api.model
    def scan_alerts(self, days_ahead=30):
        today = date.today()
        end_date = today + relativedelta(days=days_ahead)
        created = 0

        equipments = self.env['it.equipment'].search([
            ('warranty_date', '!=', False),
            ('warranty_date', '>=', today),
            ('warranty_date', '<=', end_date),
            ('state', 'not in', ['retired']),
        ])
        for eq in equipments:
            existing = self.search([
                ('alert_type', '=', 'warranty'),
                ('equipment_id', '=', eq.id),
                ('state', '=', 'pending'),
            ])
            if not existing:
                self.create({
                    'name': _('Garantie expirant - %s') % eq.name,
                    'alert_type': 'warranty',
                    'equipment_id': eq.id,
                    'old_date': eq.warranty_date,
                    'alert_date': today,
                    'days_before_expiry': (eq.warranty_date - today).days,
                })
                created += 1

        contracts = self.env['it.contract'].search([
            ('state', '=', 'active'),
            ('end_date', '!=', False),
            ('end_date', '>=', today),
            ('end_date', '<=', end_date),
        ])
        for ct in contracts:
            existing = self.search([
                ('alert_type', '=', 'contract'),
                ('contract_id', '=', ct.id),
                ('state', '=', 'pending'),
            ])
            if not existing:
                self.create({
                    'name': _('Contrat expirant - %s') % ct.name,
                    'alert_type': 'contract',
                    'contract_id': ct.id,
                    'old_date': ct.end_date,
                    'alert_date': today,
                    'days_before_expiry': (ct.end_date - today).days,
                })
                created += 1

        return created

    def action_open_related(self):
        self.ensure_one()
        if self.alert_type == 'warranty' and self.equipment_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'it.equipment',
                'view_mode': 'form',
                'res_id': self.equipment_id.id,
            }
        elif self.alert_type == 'contract' and self.contract_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'it.contract',
                'view_mode': 'form',
                'res_id': self.contract_id.id,
            }
        return True
