{
    'name': 'Gestion de Parc Informatique - IT_PARC',
    'version': '18.0.1.0.0',
    'category': 'Industries',
    'summary': 'Module de gestion de parc informatique pour TECHPARK CI',
    'description': """
Gestion de Parc Informatique - IT_PARC
========================================
Module Odoo 18 personnalisé développé pour TECHPARK CI.

Fonctionnalités principales :
- Gestion des équipements informatiques avec workflow (Brouillon → Affecté → En maintenance → Retiré)
- Affectation des équipements aux employés et départements
- Suivi des interventions de maintenance (préventive et corrective)
- Gestion des contrats fournisseurs avec alertes d'expiration
- Alertes automatiques (garanties, contrats)
- Import CSV des équipements
- Rapports PDF (fiche équipement, inventaire, maintenances)
- Exports Excel (inventaire, coûts, contrats)
- Dashboard OWL avec indicateurs clés
    """,
    'author': 'TECHPARK CI - DSI',
    'website': 'https://www.techparkci.com',
    'depends': [
        'base',
        'hr',
        'stock',
        'purchase',
        'account',
        'maintenance',
        'mail',
        'contacts',
        'web',
    ],
    'data': [
        'security/it_security.xml',
        'security/ir.model.access.csv',
        'data/it_sequence.xml',
        'data/it_cron.xml',
        'views/it_equipment_views.xml',
        'views/it_employee_assignment_views.xml',
        'views/it_intervention_views.xml',
        'views/it_contract_views.xml',
        'views/it_alert_views.xml',
        'views/it_menu.xml',
        'views/it_dashboard_views.xml',
        'views/it_dashboard_template.xml',
        'views/it_excel_actions.xml',
        'wizards/wizard_views.xml',
        'report/it_equipment_report_templates.xml',
        'report/it_inventory_report_templates.xml',
        'report/it_maintenance_report_templates.xml',
    ],
    'demo': [
        'data/it_parc_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'it_parc/static/src/js/dashboard.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
