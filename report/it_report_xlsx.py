from odoo import models, fields, api, _
from odoo.exceptions import UserError
import xlsxwriter
import io
import base64
from datetime import date, timedelta


class ItEquipmentXlsx(models.Model):
    _inherit = 'it.equipment'

    def export_inventory_xlsx(self):
        workbook = io.BytesIO()
        book = xlsxwriter.Workbook(workbook, {'in_memory': True})
        sheet = book.add_worksheet(_('Inventaire'))

        header_format = book.add_format({
            'bold': True, 'bg_color': '#2C3E50', 'font_color': 'white',
            'border': 1, 'text_wrap': True, 'valign': 'vcenter',
        })
        date_format = book.add_format({'num_format': 'dd/mm/yyyy', 'border': 1})
        money_format = book.add_format({'num_format': '#,##0', 'border': 1})
        text_format = book.add_format({'border': 1})
        title_format = book.add_format({'bold': True, 'font_size': 14})

        sheet.merge_range('A1:N1', _('Inventaire du Parc Informatique'), title_format)
        sheet.set_column('A:A', 12)
        sheet.set_column('B:B', 25)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 15)
        sheet.set_column('H:H', 12)
        sheet.set_column('I:I', 15)
        sheet.set_column('J:J', 15)
        sheet.set_column('K:K', 15)
        sheet.set_column('L:L', 15)
        sheet.set_column('M:M', 12)
        sheet.set_column('N:N', 20)

        headers = [_('Code'), _('Nom'), _('Catégorie'), _('Marque'), _('Modèle'),
                   _('N° Série'), _('Employé'), _('Département'), _('Site'),
                   _('Statut'), _("Date d'achat"), _('Fin garantie'),
                   _('Valeur'), _('Localisation')]
        for col, h in enumerate(headers):
            sheet.write(2, col, h, header_format)

        equipments = self.search([])
        for row, eq in enumerate(equipments, start=3):
            sheet.write(row, 0, eq.code or '', text_format)
            sheet.write(row, 1, eq.name or '', text_format)
            sheet.write(row, 2, eq.category_id.name or '', text_format)
            sheet.write(row, 3, eq.brand or '', text_format)
            sheet.write(row, 4, eq.model or '', text_format)
            sheet.write(row, 5, eq.serial_number or '', text_format)
            sheet.write(row, 6, eq.employee_id.name or '', text_format)
            sheet.write(row, 7, eq.department_id.name or '', text_format)
            sheet.write(row, 8, dict(eq._fields['site'].selection).get(eq.site, ''), text_format)
            sheet.write(row, 9, dict(eq._fields['state'].selection).get(eq.state, ''), text_format)
            if eq.purchase_date:
                sheet.write_datetime(row, 10, fields.Date.from_string(eq.purchase_date), date_format)
            else:
                sheet.write(row, 10, '', text_format)
            if eq.warranty_date:
                sheet.write_datetime(row, 11, fields.Date.from_string(eq.warranty_date), date_format)
            else:
                sheet.write(row, 11, '', text_format)
            sheet.write(row, 12, eq.purchase_value or 0, money_format)
            sheet.write(row, 13, eq.location or '', text_format)

        book.close()
        workbook.seek(0)
        file_data = base64.b64encode(workbook.read()).decode()

        attachment = self.env['ir.attachment'].create({
            'name': _('inventaire_parc_%s.xlsx') % fields.Date.today(),
            'type': 'binary',
            'datas': file_data,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }


class ItInterventionXlsx(models.Model):
    _inherit = 'it.intervention'

    def export_maintenance_costs_xlsx(self):
        workbook = io.BytesIO()
        book = xlsxwriter.Workbook(workbook, {'in_memory': True})
        sheet = book.add_worksheet(_('Coûts Maintenance'))

        header_format = book.add_format({
            'bold': True, 'bg_color': '#2C3E50', 'font_color': 'white',
            'border': 1, 'text_wrap': True,
        })
        date_format = book.add_format({'num_format': 'dd/mm/yyyy', 'border': 1})
        money_format = book.add_format({'num_format': '#,##0', 'border': 1})
        text_format = book.add_format({'border': 1})
        title_format = book.add_format({'bold': True, 'font_size': 14})

        sheet.merge_range('A1:G1', _('Synthèse des coûts de maintenance'), title_format)
        sheet.set_column('A:A', 12)
        sheet.set_column('B:B', 25)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 12)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 12)

        headers = [_('Équipement'), _('Intervention'), _('Technicien'), _('Type'),
                   _('Date début'), _('Durée (h)'), _('Coût')]
        for col, h in enumerate(headers):
            sheet.write(2, col, h, header_format)

        interventions = self.search([], order='equipment_id, start_date')
        for row, inv in enumerate(interventions, start=3):
            sheet.write(row, 0, inv.equipment_id.name or '', text_format)
            sheet.write(row, 1, inv.name or '', text_format)
            sheet.write(row, 2, inv.technician_id.name or '', text_format)
            sheet.write(row, 3, dict(inv._fields['intervention_type'].selection).get(inv.intervention_type, ''), text_format)
            if inv.start_date:
                sheet.write_datetime(row, 4, fields.Datetime.from_string(inv.start_date), date_format)
            else:
                sheet.write(row, 4, '', text_format)
            sheet.write(row, 5, inv.duration_hours or 0, text_format)
            sheet.write(row, 6, inv.cost or 0, money_format)

        book.close()
        workbook.seek(0)
        file_data = base64.b64encode(workbook.read()).decode()

        attachment = self.env['ir.attachment'].create({
            'name': _('couts_maintenance_%s.xlsx') % fields.Date.today(),
            'type': 'binary',
            'datas': file_data,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }


class ItContractXlsx(models.Model):
    _inherit = 'it.contract'

    def export_expiring_contracts_xlsx(self):
        today = date.today()
        end_date = today + timedelta(days=60)
        contracts = self.search([('end_date', '>=', today), ('end_date', '<=', end_date), ('state', '=', 'active')])

        workbook = io.BytesIO()
        book = xlsxwriter.Workbook(workbook, {'in_memory': True})
        sheet = book.add_worksheet(_('Contrats expirants'))

        header_format = book.add_format({
            'bold': True, 'bg_color': '#2C3E50', 'font_color': 'white',
            'border': 1, 'text_wrap': True,
        })
        date_format = book.add_format({'num_format': 'dd/mm/yyyy', 'border': 1})
        money_format = book.add_format({'num_format': '#,##0', 'border': 1})
        text_format = book.add_format({'border': 1})
        red_format = book.add_format({'border': 1, 'bg_color': '#FF6B6B', 'font_color': 'white', 'bold': True})
        orange_format = book.add_format({'border': 1, 'bg_color': '#FFA94D'})
        title_format = book.add_format({'bold': True, 'font_size': 14})

        sheet.merge_range('A1:F1', _('Contrats expirant dans les 60 jours'), title_format)
        sheet.set_column('A:A', 25)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 15)

        headers = [_('Contrat'), _('Fournisseur'), _('Type'), _('Date début'),
                   _('Date fin'), _('Montant')]
        for col, h in enumerate(headers):
            sheet.write(2, col, h, header_format)

        for row, ct in enumerate(contracts, start=3):
            days_left = (ct.end_date - today).days if ct.end_date else 0
            fmt = red_format if days_left <= 15 else (orange_format if days_left <= 30 else text_format)

            sheet.write(row, 0, ct.name or '', fmt)
            sheet.write(row, 1, ct.partner_id.name or '', fmt)
            sheet.write(row, 2, dict(ct._fields['contract_type'].selection).get(ct.contract_type, ''), fmt)
            if ct.start_date:
                sheet.write_datetime(row, 3, fields.Date.from_string(ct.start_date), date_format)
            else:
                sheet.write(row, 3, '', fmt)
            if ct.end_date:
                sheet.write_datetime(row, 4, fields.Date.from_string(ct.end_date), date_format)
            else:
                sheet.write(row, 4, '', fmt)
            sheet.write(row, 5, ct.amount or 0, money_format)

        book.close()
        workbook.seek(0)
        file_data = base64.b64encode(workbook.read()).decode()

        attachment = self.env['ir.attachment'].create({
            'name': _('contrats_expirants_%s.xlsx') % fields.Date.today(),
            'type': 'binary',
            'datas': file_data,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }
