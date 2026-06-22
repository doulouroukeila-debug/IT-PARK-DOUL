from odoo import http, fields, _
from odoo.http import request
import io
import xlsxwriter


class ItExcelExport(http.Controller):

    def _write_inventory_xlsx(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Inventaire')

        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#0066CC', 'font_color': 'white',
            'border': 1, 'text_wrap': True,
        })
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy', 'border': 1})
        money_format = workbook.add_format({'num_format': '#,##0', 'border': 1})
        cell_format = workbook.add_format({'border': 1})

        headers = [
            'Code', 'Nom', 'Catégorie', 'Marque', 'Modèle',
            'N° Série', 'N° Inventaire', 'Employé', 'Département',
            'Localisation', "Valeur d'achat", "Date d'achat",
            'Fin garantie', 'État',
        ]
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        worksheet.set_column(0, len(headers) - 1, 18)

        equipments = request.env['it.equipment'].search([])
        category_dict = dict(equipments.fields_get(['category'])['category']['selection'])
        state_dict = dict(equipments.fields_get(['state'])['state']['selection'])

        for row, eq in enumerate(equipments, start=1):
            worksheet.write(row, 0, eq.code or '', cell_format)
            worksheet.write(row, 1, eq.name or '', cell_format)
            worksheet.write(row, 2, category_dict.get(eq.category, ''), cell_format)
            worksheet.write(row, 3, eq.brand or '', cell_format)
            worksheet.write(row, 4, eq.model or '', cell_format)
            worksheet.write(row, 5, eq.serial_number or '', cell_format)
            worksheet.write(row, 6, eq.asset_number or '', cell_format)
            worksheet.write(row, 7, eq.employee_id.name or '', cell_format)
            worksheet.write(row, 8, eq.department_id.name or '', cell_format)
            worksheet.write(row, 9, eq.location or '', cell_format)
            if eq.purchase_value:
                worksheet.write_number(row, 10, eq.purchase_value, money_format)
            else:
                worksheet.write(row, 10, '', cell_format)
            if eq.purchase_date:
                worksheet.write_datetime(row, 11, eq.purchase_date, date_format)
            else:
                worksheet.write(row, 11, '', cell_format)
            if eq.warranty_date:
                worksheet.write_datetime(row, 12, eq.warranty_date, date_format)
            else:
                worksheet.write(row, 12, '', cell_format)
            worksheet.write(row, 13, state_dict.get(eq.state, ''), cell_format)

        workbook.close()
        output.seek(0)
        return output.read()

    def _write_maintenance_costs_xlsx(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Coûts maintenance')

        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#0066CC', 'font_color': 'white',
            'border': 1,
        })
        money_format = workbook.add_format({'num_format': '#,##0', 'border': 1})
        cell_format = workbook.add_format({'border': 1})

        headers = ['Équipement', 'Catégorie', 'Mois', 'Année', 'Nombre interventions', 'Coût total']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        worksheet.set_column(0, len(headers) - 1, 22)

        interventions = request.env['it.intervention'].search([
            ('state', '=', 'done'),
        ])
        category_dict = dict(interventions.fields_get(['equipment_id'])['equipment_id'].get('selection', {}))

        data = {}
        for intv in interventions:
            if intv.date_start:
                month = intv.date_start.month
                year = intv.date_start.year
                key = (intv.equipment_id.id, intv.equipment_id.category, month, year)
                if key not in data:
                    data[key] = {'count': 0, 'cost': 0.0}
                data[key]['count'] += 1
                data[key]['cost'] += (intv.cost or 0.0)

        row = 1
        for (eq_id, category, month, year), vals in data.items():
            equipment = request.env['it.equipment'].browse(eq_id)
            worksheet.write(row, 0, equipment.name, cell_format)
            worksheet.write(row, 1, dict(equipment._fields['category'].selection).get(category, ''), cell_format)
            worksheet.write(row, 2, month, cell_format)
            worksheet.write(row, 3, year, cell_format)
            worksheet.write_number(row, 4, vals['count'], cell_format)
            worksheet.write_number(row, 5, vals['cost'], money_format)
            row += 1

        workbook.close()
        output.seek(0)
        return output.read()

    def _write_expiring_contracts_xlsx(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Contrats expirants')

        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#0066CC', 'font_color': 'white',
            'border': 1,
        })
        urgent_format = workbook.add_format({
            'bg_color': '#FF6666', 'border': 1, 'font_color': 'white', 'bold': True,
        })
        warning_format = workbook.add_format({
            'bg_color': '#FFD700', 'border': 1,
        })
        money_format = workbook.add_format({'num_format': '#,##0', 'border': 1})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy', 'border': 1})
        cell_format = workbook.add_format({'border': 1})

        headers = [
            'Intitulé', 'Fournisseur', 'Type', 'Date début', 'Date fin',
            'Jours restants', 'Montant',
        ]
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        worksheet.set_column(0, len(headers) - 1, 22)

        contracts = request.env['it.contract'].search([
            ('state', '=', 'active'),
            ('date_end', '!=', False),
        ])
        type_dict = dict(contracts.fields_get(['type'])['type']['selection'])

        row = 1
        for ct in contracts:
            days_left = (ct.date_end - fields.Date.today()).days if ct.date_end else 0
            if 0 < days_left <= 60:
                fmt = urgent_format if days_left <= 15 else warning_format
            else:
                fmt = cell_format

            worksheet.write(row, 0, ct.name, fmt)
            worksheet.write(row, 1, ct.supplier_id.name or '', fmt)
            worksheet.write(row, 2, type_dict.get(ct.type, ''), fmt)
            if ct.date_start:
                worksheet.write_datetime(row, 3, ct.date_start, date_format)
            else:
                worksheet.write(row, 3, '', fmt)
            if ct.date_end:
                worksheet.write_datetime(row, 4, ct.date_end, date_format)
            else:
                worksheet.write(row, 4, '', fmt)
            worksheet.write_number(row, 5, days_left, fmt)
            if ct.amount:
                worksheet.write_number(row, 6, ct.amount, money_format)
            else:
                worksheet.write(row, 6, '', fmt)
            row += 1

        workbook.close()
        output.seek(0)
        return output.read()

    @http.route('/it_parc/export/inventory', type='http', auth='user')
    def export_inventory_xlsx(self):
        content = self._write_inventory_xlsx()
        headers = [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('Content-Disposition', 'attachment; filename="inventaire_parc.xlsx"'),
        ]
        return request.make_response(content, headers=headers)

    @http.route('/it_parc/export/maintenance_costs', type='http', auth='user')
    def export_maintenance_costs_xlsx(self):
        content = self._write_maintenance_costs_xlsx()
        headers = [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('Content-Disposition', 'attachment; filename="couts_maintenance.xlsx"'),
        ]
        return request.make_response(content, headers=headers)

    @http.route('/it_parc/export/contracts', type='http', auth='user')
    def export_contracts_xlsx(self):
        content = self._write_expiring_contracts_xlsx()
        headers = [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('Content-Disposition', 'attachment; filename="contrats_expirants.xlsx"'),
        ]
        return request.make_response(content, headers=headers)
