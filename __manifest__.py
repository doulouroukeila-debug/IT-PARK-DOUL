{
    'name': 'Gestion de Parc Informatique - IT_PARC',
    'version': '1.0.0',
    'category': 'Industries',
    'summary': 'Module de gestion de parc informatique pour TECHPARK CI',
    'description': """
Module IT_PARC - Gestion de Parc Informatique
==============================================
Module personnalisé développé pour TECHPARK CI (Abidjan, Côte d'Ivoire).

Fonctionnalités principales:
- Gestion des équipements informatiques avec workflow (Brouillon → Affecté → En maintenance → Retiré)
- Affectation des équipements aux employés et départements avec historique
- Suivi des interventions de maintenance (préventive et corrective)
- Gestion des contrats fournisseurs avec alertes d'expiration
- Alertes automatiques pour garanties et contrats
- Import CSV en masse des équipements
- Rapports PDF (QWeb) : fiche équipement, inventaire, historique maintenances
- Exports Excel : inventaire, coûts de maintenance, contrats expirants
- Tableau de bord OWL avec KPIs et graphiques
    """,
    'author': 'TECHPARK CI - DSI',
    'website': 'https://www.techpark.ci',
    'depends': [
        'base',
        'hr',
        'mail',
        'contacts',
        'stock',
        'purchase',
        'account',
        'maintenance',
        'web',
    ],
    'data': [
        'security/it_security_groups.xml',
        'security/ir.model.access.csv',
        'security/it_record_rules.xml',
        'data/it_sequence.xml',
        'data/it_cron.xml',
        'data/it_equipment_category.xml',
        'views/it_equipment_views.xml',
        'views/it_assignment_views.xml',
        'views/it_intervention_views.xml',
        'views/it_contract_views.xml',
        'views/it_alert_views.xml',
        'views/it_dashboard_views.xml',
        'views/it_menu_views.xml',
        'wizards/it_reassign_wizard_views.xml',
        'wizards/it_renew_contract_wizard_views.xml',
        'wizards/it_csv_import_wizard_views.xml',
        'wizards/it_scan_alert_wizard_views.xml',
        'report/it_report_actions.xml',
        'report/it_report_templates.xml',
    ],
    'demo': [
        'data/it_parc_demo.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'it_parc/static/src/components/dashboard/dashboard.js',
            'it_parc/static/src/components/dashboard/dashboard.xml',
            'it_parc/static/src/components/dashboard/dashboard.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
