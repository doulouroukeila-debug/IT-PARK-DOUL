from odoo import models, api


class ReportItInventory(models.AbstractModel):
    _name = 'report.it_parc.report_it_inventory'
    _description = 'Rapport inventaire PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = []
        if data and data.get('department_id'):
            domain.append(('department_id', '=', data['department_id']))
        if data and data.get('category'):
            domain.append(('category', '=', data['category']))

        docs = self.env['it.equipment'].search(domain)

        return {
            'doc_ids': docids,
            'doc_model': 'it.equipment',
            'docs': docs,
            'data': data,
        }
