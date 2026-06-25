# Module IT_PARC - Gestion de Parc Informatique

Module Odoo 18 Enterprise personnalisé développé pour **TECHPARK CI** (Abidjan, Côte d'Ivoire).

## Fonctionnalités

- **Gestion des équipements** : Workflow Brouillon → Affecté → En maintenance → Retiré
- **Affectation aux employés** : Liaison employé/département avec historique complet + assistant de réaffectation
- **Suivi des interventions** : Maintenance corrective/préventive, durée calculée automatiquement, coût, vue calendrier
- **Contrats fournisseurs** : Suivi des contrats, jours restants, assistant de renouvellement
- **Alertes automatiques** : Alertes pour garanties et contrats expirant, scan manuel et automatique (ir.cron)
- **Import CSV** : Import en masse avec détection des doublons par numéro de série
- **Rapports PDF (QWeb)** : Fiche équipement, inventaire complet, historique maintenances
- **Exports Excel (xlsxwriter)** : Inventaire, coûts maintenance, contrats expirants (60j) avec couleurs conditionnelles
- **Dashboard OWL** : 8 KPIs, graphique barres, navigation cliquable

## Dépendances

- base, hr, mail, contacts, stock, purchase, account, maintenance, web

## Installation

```bash
pip install xlsxwriter
# Copier le module dans le répertoire addons d'Odoo
./odoo-bin -u it_parc --addons-path=.../
```

## Sécurité

- **IT Technicien** : Lecture seule (équipements, contrats) + création d'interventions
- **IT Manager** : Accès complet à toutes les fonctionnalités

## Structure

```
it_parc/
├── models/          # Modèles Python
├── views/           # Vues XML (tree, form, search, kanban, calendar...)
├── wizards/         # Assistants (réaffectation, renouvellement, import CSV, scan alertes)
├── report/          # Rapports QWeb PDF + exports Excel
├── security/        # Groupes, ACLs, règles d'enregistrement
├── data/            # Données démo, séquences, cron, catégories
└── static/          # OWL Dashboard
```

## Utilisation

1. Menu **Parc Informatique** > **Tableau de bord** pour les KPIs
2. Menu **Parc Informatique** > **Équipements** pour la gestion du parc
3. Menu **Parc Informatique** > **Interventions** avec vue calendrier
4. Menu **Parc Informatique** > **Alertes** pour les échéances
5. Menu **Parc Informatique** > **Outils** > **Import CSV**
6. Boutons **Imprimer** sur chaque liste pour les rapports PDF
7. Boutons **Exporter** (Excel) sur les listes d'équipements, interventions et contrats

## Développé par

TECHPARK CI - Direction des Systèmes d'Information
Abidjan-Cocody, juin 2026
