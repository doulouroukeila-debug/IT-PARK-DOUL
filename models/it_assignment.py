from odoo import models, fields, api, _
from datetime import date


class ItAssignment(models.Model):
    _name = 'it.assignment'
    _description = 'Affectation d\'équipement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'assignment_date desc, id desc'

    equipment_id = fields.Many2one('it.equipment', string='Équipement', required=True, ondelete='cascade', tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employé', required=True, tracking=True)
    department_id = fields.Many2one('hr.department', string='Département', required=True, tracking=True)
    assignment_date = fields.Date(string="Date d'affectation", required=True, default=fields.Date.today, tracking=True)
    end_date = fields.Date(string='Date de fin', tracking=True)
    reason = fields.Text(string='Motif', tracking=True)

    state = fields.Selection([
        ('active', 'Active'),
        ('ended', 'Terminée'),
    ], string='Statut', default='active', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        assignments = super().create(vals_list)
        for assignment in assignments:
            assignment.equipment_id.state = 'assigned'
            old_assignments = self.search([
                ('equipment_id', '=', assignment.equipment_id.id),
                ('state', '=', 'active'),
                ('id', '!=', assignment.id),
            ])
            old_assignments.write({'state': 'ended', 'end_date': assignment.assignment_date or date.today()})
        return assignments

    def action_terminate(self):
        self.write({'state': 'ended', 'end_date': fields.Date.today()})
        other_active = self.search([
            ('equipment_id', '=', self.equipment_id.id),
            ('state', '=', 'active'),
            ('id', '!=', self.id),
        ])
        if not other_active:
            self.equipment_id.state = 'draft'
