from odoo import models, fields, api, _


class ItReassignWizard(models.TransientModel):
    _name = 'it.reassign.wizard'
    _description = 'Assistant de réaffectation'

    equipment_id = fields.Many2one('it.equipment', string='Équipement', required=True, readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Nouvel employé', required=True)
    department_id = fields.Many2one('hr.department', string='Nouveau département', required=True)
    reason = fields.Text(string='Motif de la réaffectation', required=True)
    assignment_date = fields.Date(string="Date d'affectation", required=True, default=fields.Date.today)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id and self.employee_id.department_id:
            self.department_id = self.employee_id.department_id

    def action_reassign(self):
        self.ensure_one()
        self.env['it.assignment'].create({
            'equipment_id': self.equipment_id.id,
            'employee_id': self.employee_id.id,
            'department_id': self.department_id.id,
            'assignment_date': self.assignment_date,
            'reason': self.reason,
        })
        return {'type': 'ir.actions.act_window_close'}
