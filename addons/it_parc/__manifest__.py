{
    'name': 'Gestion de Parc Informatique - IT_PARC',
    'version': '18.0.1.0.0',
    'category': 'Industries',
    'summary': 'Gestion de parc informatique pour TECHPARK CI',
    'depends': ['base', 'hr', 'mail', 'web'],
    'data': [
        'security/it_security.xml',
        'security/ir.model.access.csv',
        'views/it_equipment_views.xml',
        'views/it_menu.xml',
    ],
    'demo': ['data/it_parc_demo.xml'],
    'assets': {
        'web.assets_backend': ['it_parc/static/src/js/dashboard.js'],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
