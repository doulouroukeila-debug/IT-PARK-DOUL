from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class ItEquipment(models.Model):
    _name = 'it.equipment'
    _description = 'Équipement Informatique'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'create_date desc'

    name = fields.Char(string='Nom', required=True, tracking=True)
    code = fields.Char(string='Code interne', required=True, copy=False, readonly=True,
                       default=lambda self: _('Nouveau'))
    category = fields.Selection([
        ('workstation', 'Poste de travail'),
        ('server', 'Serveur'),
        ('printer', 'Imprimante'),
        ('network', 'Équipement réseau'),
        ('phone', 'Téléphone IP'),
        ('other', 'Autre'),
    ], string='Catégorie', required=True, tracking=True)
    brand = fields.Char(string='Marque', tracking=True)
    model = fields.Char(string='Modèle', tracking=True)
    serial_number = fields.Char(string='Numéro de série', tracking=True, copy=False)
    asset_number = fields.Char(string="Numéro d'inventaire", tracking=True, copy=False)

    technical_specs = fields.Text(string='Caractéristiques techniques')

    purchase_value = fields.Monetary(string="Valeur d'achat", currency_field='currency_id',
                                     tracking=True)
    currency_id = fields.Many2one('res.currency', string='Devise',
                                  default=lambda self: self.env.company.currency_id)

    purchase_date = fields.Date(string="Date d'achat", tracking=True)
    warranty_date = fields.Date(string='Date de fin de garantie', tracking=True)
    warranty_days_remaining = fields.Integer(string='Jours restants garantie',
                                             compute='_compute_warranty_days_remaining',
                                             store=True)
    warranty_expired = fields.Boolean(string='Garantie expirée',
                                      compute='_compute_warranty_expired', store=True)

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('assigned', 'Affecté'),
        ('maintenance', 'En maintenance'),
        ('retired', 'Retiré'),
    ], string='État', default='draft', tracking=True, required=True)

    employee_id = fields.Many2one('hr.employee', string='Employé affecté',
                                  compute='_compute_current_employee', store=True,
                                  tracking=True)
    department_id = fields.Many2one('hr.department', string='Département',
                                    compute='_compute_current_employee', store=True,
                                    tracking=True)
    location = fields.Char(string='Localisation', tracking=True)

    assignment_ids = fields.One2many('it.assignment', 'equipment_id',
                                     string='Affectations')
    intervention_ids = fields.One2many('it.intervention', 'equipment_id',
                                       string='Interventions')
    contract_ids = fields.Many2many(
        'it.contract',
        'it_contract_equipment_rel',
        'equipment_id',
        'contract_id',
        string='Contrats associés',
    )

    intervention_count = fields.Integer(string="Nombre d'interventions",
                                        compute='_compute_intervention_count')
    last_intervention_date = fields.Date(string='Dernière intervention',
                                         compute='_compute_last_intervention_date')

    notes = fields.Text(string='Notes internes')
    active = fields.Boolean(string='Actif', default=True)

    company_id = fields.Many2one('res.company', string='Société',
                                 default=lambda self: self.env.company)

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Le code interne doit être unique.'),
        ('serial_unique', 'UNIQUE(serial_number)',
         'Le numéro de série doit être unique.'),
    ]

    @api.model
    def create(self, vals):
        if vals.get('code', _('Nouveau')) == _('Nouveau'):
            vals['code'] = self.env['ir.sequence'].next_by_code('it.equipment') or _('Nouveau')
        return super().create(vals)

    @api.depends('warranty_date')
    def _compute_warranty_days_remaining(self):
        today = fields.Date.today()
        for rec in self:
            if rec.warranty_date:
                delta = rec.warranty_date - today
                rec.warranty_days_remaining = delta.days
            else:
                rec.warranty_days_remaining = 0

    @api.depends('warranty_date')
    def _compute_warranty_expired(self):
        today = fields.Date.today()
        for rec in self:
            rec.warranty_expired = bool(rec.warranty_date and rec.warranty_date < today)

    @api.depends('assignment_ids', 'assignment_ids.state')
    def _compute_current_employee(self):
        for rec in self:
            active_assignment = rec.assignment_ids.filtered(
                lambda a: a.state == 'active'
            )
            if active_assignment:
                rec.employee_id = active_assignment[0].employee_id
                rec.department_id = active_assignment[0].department_id
            else:
                rec.employee_id = False
                rec.department_id = False

    def _compute_intervention_count(self):
        for rec in self:
            rec.intervention_count = len(rec.intervention_ids)

    def _compute_last_intervention_date(self):
        for rec in self:
            interventions = rec.intervention_ids.sorted(key=lambda i: i.date_start,
                                                        reverse=True)
            rec.last_intervention_date = interventions[
                0].date_start if interventions else False

    def action_assign(self):
        return {
            'name': _('Affecter un équipement'),
            'type': 'ir.actions.act_window',
            'res_model': 'it.reassign.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_equipment_id': self.id},
        }

    def action_maintenance(self):
        return {
            'name': _('Créer une intervention'),
            'type': 'ir.actions.act_window',
            'res_model': 'it.intervention',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_equipment_id': self.id},
        }

    def action_retire(self):
        for rec in self:
            active_assignments = rec.assignment_ids.filtered(lambda a: a.state == 'active')
            active_assignments.write({'state': 'inactive', 'date_end': fields.Date.today()})
            rec.state = 'retired'

    def action_draft(self):
        self.state = 'draft'

    @api.model
    def get_dashboard_data(self):
        today = fields.Date.today()
        Equipment = self.env['it.equipment']
        Intervention = self.env['it.intervention']
        Contract = self.env['it.contract']
        Alert = self.env['it.alert']

        total_equipments = Equipment.search_count([])
        assigned_equipments = Equipment.search_count([('state', '=', 'assigned')])
        maintenance_equipments = Equipment.search_count([('state', '=', 'maintenance')])
        retired_equipments = Equipment.search_count([('state', '=', 'retired')])
        draft_equipments = Equipment.search_count([('state', '=', 'draft')])

        active_contracts = Contract.search_count([('state', '=', 'active')])
        expiring_contracts = Contract.search_count([
            ('state', '=', 'active'),
            ('date_end', '<=', today + timedelta(days=60)),
            ('date_end', '>=', today),
        ])
        expired_warranties = Equipment.search_count([
            ('warranty_expired', '=', True),
            ('state', '!=', 'retired'),
        ])

        pending_alerts = Alert.search_count([('state', '=', 'pending')])

        this_year = today.year
        interventions_this_year = Intervention.search_count([
            ('date_start', '>=', fields.Datetime.to_datetime(f'{this_year}-01-01 00:00:00')),
            ('date_start', '<=', fields.Datetime.to_datetime(f'{this_year}-12-31 23:59:59')),
            ('state', '=', 'done'),
        ])

        total_maintenance_cost = sum(
            Intervention.search([
                ('state', '=', 'done'),
                ('date_start', '>=', fields.Datetime.to_datetime(f'{this_year}-01-01 00:00:00')),
                ('date_start', '<=', fields.Datetime.to_datetime(f'{this_year}-12-31 23:59:59')),
            ]).mapped('cost') or [0.0]
        )

        total_asset_value = sum(Equipment.search([]).mapped('purchase_value') or [0.0])

        equipments_by_state = {
            'Brouillon': draft_equipments,
            'Affecté': assigned_equipments,
            'En maintenance': maintenance_equipments,
            'Retiré': retired_equipments,
        }

        equipments_by_category_data = Equipment.read_group(
            [('state', '!=', 'retired')],
            ['category', 'id:count'],
            ['category'],
        )
        equipments_by_category = {}
        category_dict = dict(Equipment.fields_get(['category'])['category']['selection'])
        for row in equipments_by_category_data:
            label = category_dict.get(row['category'], row['category'])
            equipments_by_category[label] = row['id:count']

        return {
            'total_equipments': total_equipments,
            'assigned_equipments': assigned_equipments,
            'maintenance_equipments': maintenance_equipments,
            'retired_equipments': retired_equipments,
            'draft_equipments': draft_equipments,
            'active_contracts': active_contracts,
            'expiring_contracts': expiring_contracts,
            'expired_warranties': expired_warranties,
            'pending_alerts': pending_alerts,
            'interventions_this_year': interventions_this_year,
            'total_maintenance_cost': total_maintenance_cost,
            'total_asset_value': total_asset_value,
            'equipments_by_state': equipments_by_state,
            'equipments_by_category': equipments_by_category,
        }
