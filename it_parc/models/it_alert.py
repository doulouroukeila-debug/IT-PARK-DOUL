from odoo import models, fields, api, _
from datetime import date, datetime, timedelta


class ItAlert(models.Model):
    _name = 'it.alert'
    _description = 'Alerte'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'
    _order = 'date_alert desc'

    display_name = fields.Char(string='Affichage', compute='_compute_display_name',
                               store=True)
    equipment_id = fields.Many2one('it.equipment', string='Équipement',
                                   tracking=True)
    contract_id = fields.Many2one('it.contract', string='Contrat', tracking=True)
    type = fields.Selection([
        ('warranty', 'Fin de garantie'),
        ('contract', 'Expiration de contrat'),
    ], string="Type d'alerte", required=True, tracking=True)
    date_alert = fields.Date(string="Date d'alerte", required=True,
                             default=fields.Date.today, tracking=True)
    date_event = fields.Date(string='Date de l\'événement', required=True,
                             tracking=True)
    days_before = fields.Integer(string='Jours avant expiration',
                                 compute='_compute_days_before', store=True)
    message = fields.Text(string='Message', required=True)
    state = fields.Selection([
        ('pending', 'En attente'),
        ('sent', 'Envoyée'),
        ('resolved', 'Résolue'),
    ], string='État', default='pending', tracking=True, required=True)

    company_id = fields.Many2one('res.company', string='Société',
                                 default=lambda self: self.env.company)

    @api.depends('type', 'equipment_id', 'contract_id')
    def _compute_display_name(self):
        for rec in self:
            if rec.type == 'warranty' and rec.equipment_id:
                rec.display_name = _(f'Alerte garantie - {rec.equipment_id.name}')
            elif rec.type == 'contract' and rec.contract_id:
                rec.display_name = _(f'Alerte contrat - {rec.contract_id.name}')
            else:
                rec.display_name = _('Alerte')

    @api.depends('date_event')
    def _compute_days_before(self):
        today = fields.Date.today()
        for rec in self:
            if rec.date_event:
                delta = rec.date_event - today
                rec.days_before = delta.days
            else:
                rec.days_before = 0

    def action_resolve(self):
        self.state = 'resolved'

    def action_sent(self):
        self.state = 'sent'

    @api.model
    def scan_alerts(self):
        today = fields.Date.today()
        alert_days = int(
            self.env['ir.config_parameter'].get_param(
                'it_parc.alert_days_before', '30'
            )
        )
        limit_date = today + timedelta(days=alert_days)

        equipments = self.env['it.equipment'].search([
            ('warranty_date', '<=', limit_date),
            ('warranty_date', '>=', today),
            ('warranty_date', '!=', False),
            ('state', '!=', 'retired'),
        ])
        for eq in equipments:
            existing = self.search([
                ('equipment_id', '=', eq.id),
                ('type', '=', 'warranty'),
                ('state', '=', 'pending'),
            ])
            if not existing:
                self.create({
                    'equipment_id': eq.id,
                    'type': 'warranty',
                    'date_alert': today,
                    'date_event': eq.warranty_date,
                    'message': _(
                        'La garantie de l\'équipement %s expire le %s'
                    ) % (eq.name, eq.warranty_date),
                })

        contracts = self.env['it.contract'].search([
            ('date_end', '<=', limit_date),
            ('date_end', '>=', today),
            ('state', '=', 'active'),
        ])
        for ct in contracts:
            existing = self.search([
                ('contract_id', '=', ct.id),
                ('type', '=', 'contract'),
                ('state', '=', 'pending'),
            ])
            if not existing:
                self.create({
                    'contract_id': ct.id,
                    'type': 'contract',
                    'date_alert': today,
                    'date_event': ct.date_end,
                    'message': _(
                        'Le contrat %s expire le %s'
                    ) % (ct.name, ct.date_end),
                })

        return True
