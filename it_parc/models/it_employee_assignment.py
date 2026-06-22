from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ItAssignment(models.Model):
    _name = 'it.assignment'
    _description = 'Affectation d\'équipement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'
    _order = 'date_start desc'

    display_name = fields.Char(string='Affichage', compute='_compute_display_name',
                               store=True)
    equipment_id = fields.Many2one('it.equipment', string='Équipement',
                                   required=True, ondelete='cascade', tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employé', required=True,
                                  tracking=True)
    department_id = fields.Many2one('hr.department', string='Département',
                                    related='employee_id.department_id', store=True,
                                    tracking=True)
    date_start = fields.Date(string='Date de début', required=True,
                             default=fields.Date.today, tracking=True)
    date_end = fields.Date(string='Date de fin', tracking=True)
    reason = fields.Text(string='Motif', tracking=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], string='État', default='active', tracking=True, required=True)

    notes = fields.Text(string='Notes')

    company_id = fields.Many2one('res.company', string='Société',
                                 default=lambda self: self.env.company)

    @api.depends('equipment_id', 'employee_id', 'date_start')
    def _compute_display_name(self):
        for rec in self:
            eq = rec.equipment_id.name or ''
            emp = rec.employee_id.name or ''
            rec.display_name = f'{eq} -> {emp} ({rec.date_start or ""})'

    @api.constrains('employee_id', 'equipment_id', 'state')
    def _check_active_assignment(self):
        for rec in self:
            if rec.state == 'active':
                existing = self.search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('equipment_id', '=', rec.equipment_id.id),
                    ('state', '=', 'active'),
                    ('id', '!=', rec.id),
                ])
                if existing:
                    raise ValidationError(
                        _('Cet équipement est déjà affecté à cet employé.')
                    )

    def action_close(self):
        self.write({
            'state': 'inactive',
            'date_end': fields.Date.today(),
        })
