Module Odoo 18 - Gestion de Parc Informatique (it_parc)
=====================================================

Développé pour TECHPARK CI - Société de services informatiques (Abidjan, Côte d'Ivoire)

Présentation
------------
Module Odoo 18 personnalisé permettant la gestion complète du parc informatique :
équipements, affectations, interventions de maintenance, contrats fournisseurs,
alertes automatisées, rapports PDF et exports Excel.

Fonctionnalités
---------------
- **Gestion des équipements** : workflow à 4 états (Brouillon → Affecté → En maintenance → Retiré)
- **Affectations** : liaison équipement ↔ employé avec historique complet
- **Interventions** : maintenance corrective/préventive avec calcul automatique de durée
- **Contrats fournisseurs** : suivi des validités, montants et équipements couverts
- **Alertes** : surveillance automatique des garanties et contrats (tâche planifiée ir.cron)
- **Import CSV** : chargement massif avec détection des doublons par numéro de série
- **Rapports PDF** (QWeb) : fiche équipement, inventaire, historique maintenances
- **Exports Excel** (xlsxwriter) : inventaire, coûts de maintenance, contrats expirants
- **Dashboard OWL** : KPIs et graphiques en temps réel

Dépendances
-----------
- base, hr, stock, purchase, account, maintenance, mail, contacts, web

Installation
------------
1. Copier le dossier `it_parc` dans le répertoire `addons` d'Odoo
2. Installer la dépendance Python : `pip install xlsxwriter`
3. Redémarrer le serveur Odoo
4. Activer le mode développeur dans Odoo
5. Aller dans Applications → Mettre à jour la liste des modules
6. Rechercher "it_parc" et installer

Mise à jour
-----------
```bash
./odoo-bin -u it_parc -d <nom_base>
```

Groupes de sécurité
-------------------
- **IT Technicien** : accès en lecture + création d'interventions
- **IT Manager** : accès complet (création, modification, suppression)

Données de démonstration
------------------------
12 équipements, 3 contrats, 5 interventions et 3 affectations sont fournis
pour tester le module sans saisie manuelle.

Structure du module
-------------------
- models/ : modèles Python (équipement, affectation, intervention, contrat, alerte)
- views/ : vues XML (formulaires, listes, recherche, menus)
- wizards/ : assistants (réaffectation, renouvellement, scan alertes, import CSV)
- report/ : rapports QWeb PDF
- security/ : groupes d'accès et ACL
- data/ : séquences, tâche planifiée, données de démo
- controllers/ : exports Excel et API dashboard
- static/src/js/ : composant OWL du dashboard

Auteur
------
TECHPARK CI - Direction des Systèmes d'Information
Abidjan-Cocody, Côte d'Ivoire
