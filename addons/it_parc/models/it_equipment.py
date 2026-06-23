from odoo import models, fields


class ItEquipment(models.Model):
    _name = 'it.equipment'
    _description = 'Équipement Informatique'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Nom', required=True, tracking=True)
    category = fields.Selection([
        ('workstation', 'Poste de travail'),
        ('server', 'Serveur'),
        ('printer', 'Imprimante'),
        ('network', 'Équipement réseau'),
        ('phone', 'Téléphone IP'),
    ], string='Catégorie', required=True)
    serial_number = fields.Char(string='Numéro de série')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('assigned', 'Affecté'),
        ('maintenance', 'En maintenance'),
        ('retired', 'Retiré'),
    ], string='État', default='draft', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employé affecté')
    department_id = fields.Many2one('hr.department', string='Département',
                                    related='employee_id.department_id', store=True)
    warranty_date = fields.Date(string='Fin de garantie')
    purchase_value = fields.Monetary(string="Valeur d'achat",
                                     currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Devise',
                                  default=lambda self: self.env.company.currency_id)
    notes = fields.Text(string='Notes')
