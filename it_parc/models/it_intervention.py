from odoo import models, fields, api, _
from datetime import datetime


class ItIntervention(models.Model):
    _name = 'it.intervention'
    _description = 'Intervention de maintenance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'
    _order = 'date_start desc'

    display_name = fields.Char(string='Affichage', compute='_compute_display_name',
                               store=True)
    equipment_id = fields.Many2one('it.equipment', string='Équipement',
                                   required=True, tracking=True)
    type = fields.Selection([
        ('corrective', 'Corrective'),
        ('preventive', 'Préventive'),
    ], string='Type', required=True, tracking=True)
    title = fields.Char(string='Titre', required=True, tracking=True)
    description = fields.Text(string='Description')
    technician_id = fields.Many2one('hr.employee', string='Technicien',
                                    required=True, tracking=True)
    date_start = fields.Datetime(string='Date de début', required=True,
                                 default=fields.Datetime.now, tracking=True)
    date_end = fields.Datetime(string='Date de fin', tracking=True)
    duration_hours = fields.Float(string='Durée (heures)',
                                  compute='_compute_duration_hours', store=True)
    cost = fields.Monetary(string='Coût', currency_field='currency_id',
                           tracking=True)
    currency_id = fields.Many2one('res.currency', string='Devise',
                                  default=lambda self: self.env.company.currency_id)
    report = fields.Html(string='Rapport d\'intervention')
    state = fields.Selection([
        ('planned', 'Planifiée'),
        ('in_progress', 'En cours'),
        ('done', 'Terminée'),
        ('cancelled', 'Annulée'),
    ], string='État', default='planned', tracking=True, required=True)

    company_id = fields.Many2one('res.company', string='Société',
                                 default=lambda self: self.env.company)

    @api.depends('equipment_id', 'title', 'date_start')
    def _compute_display_name(self):
        for rec in self:
            eq = rec.equipment_id.name or ''
            rec.display_name = f'[{eq}] {rec.title}'

    @api.depends('date_start', 'date_end')
    def _compute_duration_hours(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                delta = rec.date_end - rec.date_start
                rec.duration_hours = delta.total_seconds() / 3600.0
            else:
                rec.duration_hours = 0.0

    def action_start(self):
        self.write({
            'state': 'in_progress',
            'date_start': fields.Datetime.now(),
        })
        if self.equipment_id.state == 'assigned':
            self.equipment_id.state = 'maintenance'

    def action_done(self):
        self.write({
            'state': 'done',
            'date_end': fields.Datetime.now(),
        })
        self.equipment_id.state = 'assigned'

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_planned(self):
        self.write({'state': 'planned'})
