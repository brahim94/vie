# -*- coding: utf-8 -*-
{
    "name": "Helpdesk Réclamation",
    'author': 'Warlock Technologies',
    "description": """Helpdesk Réclamations""",
    "summary": """Helpdesk Réclamation""",
    "version": "12.0.3.0.6",
    "support": "info@warlocktechnologies.com",
    "category": "Support",
    "depends": ['base', 'product', 'account'],
    "data": [
        'security/ir.model.access.csv',
        'security/wt_helpdesk_security.xml',
        'data/data.xml',
        'data/ir_sequence_data.xml',

        'report/helpdesk_report_templates.xml',
        'report/helpdesk_report.xml',
        'report/helpdesk_bon_retour_report_templates.xml',
        'report/helpdesk_bone_de_demarque_report.xml',
        'wizard/message_view.xml',
        'views/pannes_view.xml',
        'views/ticket_type_view.xml',
        'views/decision_view.xml',
        'views/action_client_view.xml',
        'views/action_fournisseur_view.xml',
        'views/motif_view.xml',
        'views/processus_view.xml',
        'views/articles_view.xml',
        'views/ticket_view.xml',
        'views/factures_view.xml',
        'views/synchronize_view.xml',
        'views/menu_parameters.xml',
        'views/res_partner_view.xml',
    ],
    'installable': True,
}