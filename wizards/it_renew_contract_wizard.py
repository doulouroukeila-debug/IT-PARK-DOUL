from odoo import models, fields, api, _


class ItRenewContractWizard(models.TransientModel):
    _name = 'it.renew.contract.wizard'
    _description = 'Assistant de renouvellement de contrat'

    contract_id = fields.Many2one('it.contract', string='Contrat', required=True, readonly=True)
    new_start_date = fields.Date(string='Nouvelle date de début', required=True, default=fields.Date.today)
    new_end_date = fields.Date(string='Nouvelle date de fin', required=True)
    new_amount = fields.Monetary(string='Nouveau montant', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id)
    notes = fields.Text(string='Notes')

    def action_renew(self):
        self.ensure_one()
        old = self.contract_id
        old.write({'state': 'renewed'})
        new_contract = old.copy({
            'start_date': self.new_start_date,
            'end_date': self.new_end_date,
            'amount': self.new_amount or old.amount,
            'state': 'active',
            'notes': self.notes or old.notes,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'it.contract',
            'view_mode': 'form',
            'res_id': new_contract.id,
        }
