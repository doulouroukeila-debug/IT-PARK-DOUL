from odoo import http, fields, _
from odoo.http import request
from datetime import datetime, timedelta


class ItDashboardController(http.Controller):

    @http.route('/it_parc/dashboard/data', type='json', auth='user')
    def dashboard_data(self):
        Equipment = request.env['it.equipment']
        Intervention = request.env['it.intervention']
        Contract = request.env['it.contract']
        Alert = request.env['it.alert']
        today = fields.Date.today()

        total_equipments = Equipment.search_count([])
        assigned_equipments = Equipment.search_count([('state', '=', 'assigned')])
        maintenance_equipments = Equipment.search_count([('state', '=', 'maintenance')])
        retired_equipments = Equipment.search_count([('state', '=', 'retired')])
        draft_equipments = Equipment.search_count([('state', '=', 'draft')])

        active_contracts = Contract.search_count([('state', '=', 'active')])
        expiring_contracts = Contract.search_count([
            ('state', '=', 'active'),
            ('date_end', '<=', today + timedelta(days=60)),
            ('date_end', '>=', today),
        ])
        expired_warranties = Equipment.search_count([
            ('warranty_expired', '=', True),
            ('state', '!=', 'retired'),
        ])

        pending_alerts = Alert.search_count([('state', '=', 'pending')])

        this_year = today.year
        interventions_this_year = Intervention.search_count([
            ('date_start', '>=', datetime(this_year, 1, 1)),
            ('date_start', '<=', datetime(this_year, 12, 31, 23, 59, 59)),
        ])

        total_maintenance_cost = sum(
            Intervention.search([
                ('state', '=', 'done'),
                ('date_start', '>=', datetime(this_year, 1, 1)),
                ('date_start', '<=', datetime(this_year, 12, 31, 23, 59, 59)),
            ]).mapped('cost') or [0.0]
        )

        total_asset_value = sum(Equipment.search([]).mapped('purchase_value') or [0.0])

        equipments_by_state = {
            'Brouillon': draft_equipments,
            'Affecté': assigned_equipments,
            'En maintenance': maintenance_equipments,
            'Retiré': retired_equipments,
        }

        equipments_by_category_data = Equipment.read_group(
            [('state', '!=', 'retired')],
            ['category', 'id:count'],
            ['category'],
        )
        equipments_by_category = {}
        category_dict = dict(Equipment.fields_get(['category'])['category']['selection'])
        for row in equipments_by_category_data:
            label = category_dict.get(row['category'], row['category'])
            equipments_by_category[label] = row['id:count']

        return {
            'total_equipments': total_equipments,
            'assigned_equipments': assigned_equipments,
            'maintenance_equipments': maintenance_equipments,
            'retired_equipments': retired_equipments,
            'draft_equipments': draft_equipments,
            'active_contracts': active_contracts,
            'expiring_contracts': expiring_contracts,
            'expired_warranties': expired_warranties,
            'pending_alerts': pending_alerts,
            'interventions_this_year': interventions_this_year,
            'total_maintenance_cost': total_maintenance_cost,
            'total_asset_value': total_asset_value,
            'equipments_by_state': equipments_by_state,
            'equipments_by_category': equipments_by_category,
        }
