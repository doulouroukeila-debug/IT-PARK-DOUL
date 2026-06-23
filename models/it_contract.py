from odoo import models, fields, api, _
from datetime import date


class ItContract(models.Model):
    _name = 'it.contract'
    _description = 'Contrat fournisseur'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'end_date asc, id desc'

    name = fields.Char(string='Libellé', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Fournisseur', required=True, tracking=True)
    contract_type = fields.Selection([
        ('maintenance', 'Contrat de maintenance'),
        ('license', 'Licence logicielle'),
        ('support', 'Support technique'),
        ('warranty_ext', 'Extension de garantie'),
        ('other', 'Autre'),
    ], string='Type', required=True, default='maintenance', tracking=True)

    start_date = fields.Date(string='Date de début', required=True, tracking=True)
    end_date = fields.Date(string='Date de fin', required=True, tracking=True)
    remaining_days = fields.Integer(string='Jours restants', compute='_compute_remaining_days', store=True)
    amount = fields.Monetary(string='Montant', currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id)

    contract_line_ids = fields.One2many('it.contract.line', 'contract_id', string='Équipements couverts')
    equipment_count = fields.Integer(string="Nombre d'équipements", compute='_compute_equipment_count')

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('renewed', 'Renouvelé'),
    ], string='Statut', default='active', tracking=True)

    ref = fields.Char(string='Référence contrat')
    notes = fields.Text(string='Notes')
    attachment_ids = fields.Many2many('ir.attachment', string='Documents')

    @api.depends('end_date')
    def _compute_remaining_days(self):
        today = date.today()
        for rec in self:
            if rec.end_date:
                delta = rec.end_date - today
                rec.remaining_days = delta.days if delta.days >= 0 else 0
            else:
                rec.remaining_days = 0

    @api.depends('contract_line_ids')
    def _compute_equipment_count(self):
        for rec in self:
            rec.equipment_count = len(rec.contract_line_ids)

    def action_renew(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Renouveler le contrat'),
            'res_model': 'it.renew.contract.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_contract_id': self.id},
        }

    def action_expire(self):
        self.write({'state': 'expired'})


class ItContractLine(models.Model):
    _name = 'it.contract.line'
    _description = 'Ligne de contrat - équipement couvert'

    contract_id = fields.Many2one('it.contract', string='Contrat', required=True, ondelete='cascade')
    equipment_id = fields.Many2one('it.equipment', string='Équipement', required=True)
    description = fields.Text(string='Description')
    coverage_details = fields.Text(string='Détails de couverture')
