from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import csv
import io


class ItCsvImportWizard(models.TransientModel):
    _name = 'it.csv.import.wizard'
    _description = 'Assistant import CSV'

    file = fields.Binary(string='Fichier CSV', required=True)
    filename = fields.Char(string='Nom du fichier')

    line_ids = fields.One2many('it.csv.import.line', 'wizard_id',
                                string='Résultats')
    state = fields.Selection([
        ('choose', 'Choisir'),
        ('result', 'Résultat'),
    ], string='État', default='choose')

    def action_import(self):
        self.ensure_one()
        if not self.file:
            raise UserError(_('Veuillez sélectionner un fichier CSV.'))

        try:
            data = base64.b64decode(self.file)
            reader = csv.DictReader(io.StringIO(data.decode('utf-8')))
        except Exception:
            raise UserError(_('Format de fichier invalide.'))

        created = 0
        ignored = 0
        errors = 0
        error_lines = []
        Equipment = self.env['it.equipment']
        default_category = 'other'

        for line_num, row in enumerate(reader, start=2):
            try:
                serial = row.get('serial_number', '').strip()
                name = row.get('name', '').strip()

                if not name:
                    error_lines.append(
                        f'Ligne {line_num}: Nom manquant'
                    )
                    errors += 1
                    continue

                if serial:
                    existing = Equipment.search([
                        ('serial_number', '=', serial)
                    ])
                    if existing:
                        ignored += 1
                        error_lines.append(
                            f'Ligne {line_num}: Doublon numéro de série {serial}'
                        )
                        continue

                category = row.get('category', default_category).strip()
                if category not in dict(Equipment.fields_get(
                        ['category'])['category']['selection']):
                    category = default_category

                vals = {
                    'name': name,
                    'serial_number': serial or False,
                    'category': category,
                    'brand': row.get('brand', '').strip(),
                    'model': row.get('model', '').strip(),
                    'asset_number': row.get('asset_number', '').strip(),
                    'location': row.get('location', '').strip(),
                    'purchase_value': float(row['purchase_value']) if row.get(
                        'purchase_value', '').strip() else 0.0,
                    'technical_specs': row.get('technical_specs', '').strip(),
                }
                if row.get('purchase_date', '').strip():
                    vals['purchase_date'] = row['purchase_date'].strip()
                if row.get('warranty_date', '').strip():
                    vals['warranty_date'] = row['warranty_date'].strip()

                Equipment.create(vals)
                created += 1

            except Exception as e:
                errors += 1
                error_lines.append(f'Ligne {line_num}: {str(e)}')

        lines_data = []
        for err in error_lines:
            lines_data.append((0, 0, {
                'line_content': err,
                'status': 'error',
            }))

        if created > 0:
            lines_data.insert(0, (0, 0, {
                'line_content': f'{created} équipement(s) créé(s) avec succès.',
                'status': 'success',
            }))
        if ignored > 0:
            lines_data.append((0, 0, {
                'line_content': f'{ignored} ligne(s) ignorée(s) (doublons).',
                'status': 'warning',
            }))

        self.write({
            'line_ids': lines_data,
            'state': 'result',
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'it.csv.import.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}


class ItCsvImportLine(models.TransientModel):
    _name = 'it.csv.import.line'
    _description = 'Ligne de résultat d\'import CSV'

    wizard_id = fields.Many2one('it.csv.import.wizard', string='Assistant',
                                required=True, ondelete='cascade')
    line_content = fields.Char(string='Contenu')
    status = fields.Selection([
        ('success', 'Succès'),
        ('warning', 'Attention'),
        ('error', 'Erreur'),
    ], string='Statut', default='error')
