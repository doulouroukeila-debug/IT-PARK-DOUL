from odoo import models, fields, api, _
from datetime import timedelta


class ItRenewContractWizard(models.TransientModel):
    _name = 'it.renew.contract.wizard'
    _description = 'Assistant de renouvellement de contrat'

    contract_id = fields.Many2one('it.contract', string='Contrat',
                                  required=True, readonly=True)
    date_start = fields.Date(string='Nouvelle date de début', required=True)
    date_end = fields.Date(string='Nouvelle date de fin', required=True)
    amount = fields.Monetary(string='Nouveau montant',
                             currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Devise',
                                  default=lambda self: self.env.company.currency_id)
    notes = fields.Text(string='Notes')

    @api.onchange('contract_id')
    def _onchange_contract_id(self):
        if self.contract_id:
            self.date_start = self.contract_id.date_end + timedelta(days=1)
            self.date_end = self.contract_id.date_end + timedelta(days=365)
            self.amount = self.contract_id.amount

    def action_confirm(self):
        self.ensure_one()
        contract = self.contract_id

        self.env['it.contract'].create({
            'name': contract.name + ' (Renouvelé)',
            'ref': contract.ref,
            'supplier_id': contract.supplier_id.id,
            'type': contract.type,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'amount': self.amount,
            'equipment_ids': [(6, 0, contract.equipment_ids.ids)],
            'state': 'active',
        })

        contract.state = 'expired'

        return {'type': 'ir.actions.act_window_close'}
