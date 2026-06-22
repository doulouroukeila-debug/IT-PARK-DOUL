from odoo import models, api
from datetime import datetime


class ReportItMaintenanceHistory(models.AbstractModel):
    _name = 'report.it_parc.report_it_maintenance_history'
    _description = 'Rapport historique maintenances PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = []
        if data and data.get('date_start'):
            domain.append(('date_start', '>=', data['date_start']))
        if data and data.get('date_end'):
            domain.append(('date_start', '<=', data['date_end']))

        docs = self.env['it.intervention'].search(domain, order='date_start desc')
        total_cost = sum(docs.mapped('cost'))

        return {
            'doc_ids': docids,
            'doc_model': 'it.intervention',
            'docs': docs,
            'total_cost': total_cost,
            'data': data,
        }
