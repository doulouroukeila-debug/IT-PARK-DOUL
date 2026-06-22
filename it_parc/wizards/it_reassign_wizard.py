from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ItReassignWizard(models.TransientModel):
    _name = 'it.reassign.wizard'
    _description = 'Assistant de réaffectation'

    equipment_id = fields.Many2one('it.equipment', string='Équipement',
                                   required=True, readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Nouvel employé',
                                  required=True)
    date_start = fields.Date(string='Date de début', required=True,
                             default=fields.Date.today)
    reason = fields.Text(string='Motif de la réaffectation', required=True)

    def action_confirm(self):
        self.ensure_one()
        equipment = self.equipment_id

        active_assignments = equipment.assignment_ids.filtered(
            lambda a: a.state == 'active'
        )
        active_assignments.write({
            'state': 'inactive',
            'date_end': fields.Date.today(),
        })

        self.env['it.assignment'].create({
            'equipment_id': equipment.id,
            'employee_id': self.employee_id.id,
            'department_id': self.employee_id.department_id.id,
            'date_start': self.date_start,
            'reason': self.reason,
            'state': 'active',
        })

        equipment.write({
            'state': 'assigned',
            'employee_id': self.employee_id.id,
            'department_id': self.employee_id.department_id.id,
        })

        return {'type': 'ir.actions.act_window_close'}
