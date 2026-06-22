from odoo import models, fields, api, _
from datetime import date, datetime


class ItContract(models.Model):
    _name = 'it.contract'
    _description = 'Contrat fournisseur'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'date_end asc'

    name = fields.Char(string='Intitulé du contrat', required=True, tracking=True)
    ref = fields.Char(string='Référence', tracking=True, copy=False)
    supplier_id = fields.Many2one('res.partner', string='Fournisseur',
                                  required=True, tracking=True)
    type = fields.Selection([
        ('maintenance', 'Contrat de maintenance'),
        ('license', 'Licence logicielle'),
        ('service', 'Contrat de service'),
        ('other', 'Autre'),
    ], string='Type', required=True, tracking=True)
    date_start = fields.Date(string='Date de début', required=True, tracking=True)
    date_end = fields.Date(string='Date de fin', required=True, tracking=True)
    days_remaining = fields.Integer(string='Jours restants',
                                    compute='_compute_days_remaining', store=True)
    amount = fields.Monetary(string='Montant', currency_field='currency_id',
                             tracking=True)
    currency_id = fields.Many2one('res.currency', string='Devise',
                                  default=lambda self: self.env.company.currency_id)
    equipment_ids = fields.Many2many(
        'it.equipment',
        'it_contract_equipment_rel',
        'contract_id',
        'equipment_id',
        string='Équipements couverts',
    )
    attachment_ids = fields.Many2many('ir.attachment',
                                      string='Documents contractuels')
    state = fields.Selection([
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('terminated', 'Résilié'),
    ], string='État', default='active', tracking=True, required=True)
    notes = fields.Text(string='Notes')

    company_id = fields.Many2one('res.company', string='Société',
                                 default=lambda self: self.env.company)

    @api.depends('date_end')
    def _compute_days_remaining(self):
        today = fields.Date.today()
        for rec in self:
            if rec.date_end:
                delta = rec.date_end - today
                rec.days_remaining = delta.days
            else:
                rec.days_remaining = 0

    def action_renew(self):
        return {
            'name': _('Renouveler le contrat'),
            'type': 'ir.actions.act_window',
            'res_model': 'it.renew.contract.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_contract_id': self.id},
        }

    def action_expire(self):
        self.state = 'expired'

    def action_terminate(self):
        self.state = 'terminated'
