from odoo import models, fields, api, _
from odoo.exceptions import UserError
import csv
import io
import base64
import logging

_logger = logging.getLogger(__name__)


class ItCsvImportWizard(models.TransientModel):
    _name = 'it.csv.import.wizard'
    _description = 'Assistant import CSV'

    file = fields.Binary(string='Fichier CSV', required=True)
    filename = fields.Char(string='Nom du fichier')
    report = fields.Text(string='Rapport d\'import', readonly=True)

    def action_import(self):
        self.ensure_one()
        if not self.file:
            raise UserError(_('Veuillez sélectionner un fichier CSV.'))

        try:
            data = base64.b64decode(self.file)
            reader = csv.DictReader(io.StringIO(data.decode('utf-8-sig')))
        except Exception as e:
            raise UserError(_('Erreur de lecture du fichier : %s') % str(e))

        Equipment = self.env['it.equipment']
        Category = self.env['it.equipment.category']
        created = 0
        skipped = 0
        errors = []
        line_num = 1

        for row in reader:
            line_num += 1
            serial = row.get('serial_number', '').strip()
            if not serial:
                errors.append(_('Ligne %d : numéro de série manquant') % (line_num - 1))
                continue

            existing = Equipment.search([('serial_number', '=', serial)], limit=1)
            if existing:
                skipped += 1
                continue

            cat_name = row.get('category', '').strip()
            category = Category
            if cat_name:
                category = Category.search([('name', '=', cat_name)], limit=1)
                if not category:
                    category = Category.create({'name': cat_name})

            try:
                Equipment.create({
                    'name': row.get('name', serial).strip(),
                    'serial_number': serial,
                    'category_id': category.id or False,
                    'brand': row.get('brand', '').strip(),
                    'model': row.get('model', '').strip(),
                    'processor': row.get('processor', '').strip(),
                    'ram': row.get('ram', '').strip(),
                    'storage': row.get('storage', '').strip(),
                    'os': row.get('os', '').strip(),
                    'location': row.get('location', '').strip(),
                    'site': row.get('site', 'abidjan_cocody').strip(),
                    'purchase_value': float(row.get('purchase_value', 0) or 0),
                    'purchase_date': row.get('purchase_date', False) or False,
                    'warranty_date': row.get('warranty_date', False) or False,
                    'supplier_id': False,
                    'state': row.get('state', 'draft').strip(),
                })
                created += 1
            except Exception as e:
                errors.append(_('Ligne %d : %s') % (line_num - 1, str(e)))

        report = _('Import terminé.\nLignes créées : %d\nLignes ignorées (doublons) : %d\nErreurs : %d\n') % (
            created, skipped, len(errors))
        if errors:
            report += '\n' + _('Détail des erreurs :\n') + '\n'.join(errors)

        self.write({'report': report})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'it.csv.import.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
