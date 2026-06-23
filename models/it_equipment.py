from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class ItEquipment(models.Model):
    _name = 'it.equipment'
    _description = 'Équipement informatique'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'create_date desc'

    name = fields.Char(string='Nom', required=True, tracking=True)
    code = fields.Char(string='Code interne', readonly=True, default=lambda self: _('Nouveau'))
    category_id = fields.Many2one('it.equipment.category', string='Catégorie', required=True, tracking=True)
    brand = fields.Char(string='Marque', tracking=True)
    model = fields.Char(string='Modèle', tracking=True)
    serial_number = fields.Char(string='Numéro de série', required=True, tracking=True, copy=False)
    asset_number = fields.Char(string="Numéro d'inventaire", tracking=True, copy=False)

    technical_specs = fields.Text(string='Caractéristiques techniques')
    processor = fields.Char(string='Processeur')
    ram = fields.Char(string='Mémoire RAM')
    storage = fields.Char(string='Stockage')
    os = fields.Char(string="Système d'exploitation")

    purchase_value = fields.Monetary(string="Valeur d'achat", currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id)
    purchase_date = fields.Date(string="Date d'achat", tracking=True)
    warranty_date = fields.Date(string='Date de fin de garantie', tracking=True)
    warranty_remaining_days = fields.Integer(string='Jours restants garantie', compute='_compute_warranty_remaining', store=True)

    supplier_id = fields.Many2one('res.partner', string='Fournisseur', domain="[('supplier_rank', '>', 0)]")
    location = fields.Char(string='Localisation')
    site = fields.Selection([
        ('abidjan_cocody', 'Abidjan - Cocody'),
        ('abidjan_plateau', 'Abidjan - Plateau'),
        ('bouake', 'Bouaké'),
    ], string='Site', default='abidjan_cocody', tracking=True)

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('assigned', 'Affecté'),
        ('maintenance', 'En maintenance'),
        ('retired', 'Retiré'),
    ], string='Statut', default='draft', tracking=True, group_expand='_expand_states')

    employee_id = fields.Many2one('hr.employee', string='Employé affecté', compute='_compute_current_assignment', store=True, tracking=True)
    department_id = fields.Many2one('hr.department', string='Département', compute='_compute_current_assignment', store=True, tracking=True)
    assignment_date = fields.Date(string="Date d'affectation", compute='_compute_current_assignment', store=True)

    assignment_ids = fields.One2many('it.assignment', 'equipment_id', string='Historique des affectations')
    intervention_ids = fields.One2many('it.intervention', 'equipment_id', string='Interventions')
    contract_line_ids = fields.One2many('it.contract.line', 'equipment_id', string='Lignes de contrat')

    intervention_count = fields.Integer(string='Nombre d\'interventions', compute='_compute_intervention_count')
    last_intervention_date = fields.Date(string='Dernière intervention', compute='_compute_last_intervention_date')
    total_maintenance_cost = fields.Monetary(string='Coût total maintenance', currency_field='currency_id', compute='_compute_total_maintenance_cost')

    active = fields.Boolean(string='Actif', default=True)
    notes = fields.Text(string='Notes')

    @api.model
    def _expand_states(self, states, domain, order):
        return ['draft', 'assigned', 'maintenance', 'retired']

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', _('Nouveau')) == _('Nouveau'):
                vals['code'] = self.env['ir.sequence'].next_by_code('it.equipment') or _('Nouveau')
        return super().create(vals_list)

    def action_assign(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Affecter un équipement'),
            'res_model': 'it.reassign.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_equipment_id': self.id,
                'default_employee_id': self.employee_id.id,
                'default_department_id': self.department_id.id,
            },
        }

    def action_set_maintenance(self):
        for rec in self:
            rec.state = 'maintenance'

    def action_set_retired(self):
        for rec in self:
            rec.state = 'retired'

    def action_set_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_create_intervention(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Nouvelle intervention'),
            'res_model': 'it.intervention',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_equipment_id': self.id},
        }

    @api.depends('assignment_ids', 'assignment_ids.state')
    def _compute_current_assignment(self):
        for rec in self:
            current = rec.assignment_ids.filtered(lambda a: a.state == 'active')
            if current:
                current = current.sorted(lambda a: a.assignment_date, reverse=True)[:1]
                rec.employee_id = current.employee_id
                rec.department_id = current.department_id
                rec.assignment_date = current.assignment_date
            else:
                rec.employee_id = False
                rec.department_id = False
                rec.assignment_date = False

    @api.depends('warranty_date')
    def _compute_warranty_remaining(self):
        today = date.today()
        for rec in self:
            if rec.warranty_date:
                delta = rec.warranty_date - today
                rec.warranty_remaining_days = delta.days if delta.days >= 0 else 0
            else:
                rec.warranty_remaining_days = 0

    @api.depends('intervention_ids')
    def _compute_intervention_count(self):
        for rec in self:
            rec.intervention_count = len(rec.intervention_ids)

    @api.depends('intervention_ids.end_date')
    def _compute_last_intervention_date(self):
        for rec in self:
            interventions = rec.intervention_ids.filtered(lambda i: i.end_date)
            if interventions:
                rec.last_intervention_date = max(interventions.mapped('end_date'))
            else:
                rec.last_intervention_date = False

    @api.depends('intervention_ids.cost')
    def _compute_total_maintenance_cost(self):
        for rec in self:
            rec.total_maintenance_cost = sum(rec.intervention_ids.mapped('cost') or [0.0])

    @api.constrains('serial_number')
    def _check_serial_number(self):
        for rec in self:
            if rec.serial_number:
                dup = self.search([('serial_number', '=', rec.serial_number), ('id', '!=', rec.id)])
                if dup:
                    raise ValidationError(_('Le numéro de série "%s" existe déjà.' % rec.serial_number))

    def name_get(self):
        result = []
        for rec in self:
            name = rec.code and f'[{rec.code}] {rec.name}' or rec.name
            result.append((rec.id, name))
        return result


class ItEquipmentCategory(models.Model):
    _name = 'it.equipment.category'
    _description = 'Catégorie d\'équipement'
    _order = 'sequence, name'

    name = fields.Char(string='Nom', required=True, translate=True)
    sequence = fields.Integer(string='Séquence', default=10)
    parent_id = fields.Many2one('it.equipment.category', string='Catégorie parente')
    child_ids = fields.One2many('it.equipment.category', 'parent_id', string='Sous-catégories')
    equipment_count = fields.Integer(string="Nombre d'équipements", compute='_compute_equipment_count')
    description = fields.Text(string='Description')

    @api.depends('name')
    def _compute_equipment_count(self):
        for rec in self:
            rec.equipment_count = self.env['it.equipment'].search_count([('category_id', '=', rec.id)])
