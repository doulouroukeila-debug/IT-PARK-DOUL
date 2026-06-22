from odoo import models, api


class ReportItEquipment(models.AbstractModel):
    _name = 'report.it_parc.report_it_equipment'
    _description = 'Fiche équipement PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['it.equipment'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'it.equipment',
            'docs': docs,
        }
