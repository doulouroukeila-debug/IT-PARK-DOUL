from odoo import models, fields, api, _
from datetime import timedelta


class ItIntervention(models.Model):
    _name = 'it.intervention'
    _description = 'Intervention de maintenance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'planned_date desc, id desc'

    name = fields.Char(string='Titre', required=True, tracking=True)
    equipment_id = fields.Many2one('it.equipment', string='Équipement', required=True, tracking=True)
    technician_id = fields.Many2one('hr.employee', string='Technicien', required=True, tracking=True)
    intervention_type = fields.Selection([
        ('corrective', 'Corrective'),
        ('preventive', 'Préventive'),
    ], string='Type', required=True, default='corrective', tracking=True)

    description = fields.Text(string='Description de la panne / intervention')
    report = fields.Text(string="Rapport d'intervention")

    start_date = fields.Datetime(string='Date de début', tracking=True)
    end_date = fields.Datetime(string='Date de fin', tracking=True)
    duration_hours = fields.Float(string='Durée (heures)', compute='_compute_duration', store=True, readonly=True)

    cost = fields.Monetary(string='Coût', currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id)

    state = fields.Selection([
        ('planned', 'Planifiée'),
        ('in_progress', 'En cours'),
        ('done', 'Terminée'),
        ('cancelled', 'Annulée'),
    ], string='Statut', default='planned', tracking=True)

    planned_date = fields.Date(string='Date planifiée', tracking=True)
    is_late = fields.Boolean(string='En retard', compute='_compute_late', store=True)

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                delta = rec.end_date - rec.start_date
                rec.duration_hours = delta.total_seconds() / 3600.0
            else:
                rec.duration_hours = 0.0

    @api.depends('planned_date', 'state')
    def _compute_late(self):
        today = fields.Date.today()
        for rec in self:
            if rec.state == 'planned' and rec.planned_date and rec.planned_date < today:
                rec.is_late = True
            else:
                rec.is_late = False

    def action_start(self):
        self.write({'state': 'in_progress', 'start_date': fields.Datetime.now()})

    def action_done(self):
        self.write({'state': 'done', 'end_date': fields.Datetime.now()})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_plan(self):
        self.write({'state': 'planned'})
