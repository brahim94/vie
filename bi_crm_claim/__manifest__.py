# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'CRM Claim Management',
    'version': '12.0.1.4',
    'category': 'Sales',
    'author': "TECH-IT",
    'website': 'www.tech-it.ma',
    'sequence': 5,
    'summary': 'This plugin helps to manage after sales services as claim management',
    'description': "Claim system for your product, claim management, submit claim, claim form, Ticket claim, support ticket, issue, website project issue, crm management, ticket handling,support management, project support, crm support, online support management, online claim, claim product, claim services, issue claim, fix claim, raise ticket, raise issue, view claim, display claim, list claim on website ",
    'license':'OPL-1',
    'depends': ['crm','utm','sales_team'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/claim_category_template.xml',
        'data/ir_cron_data.xml',
        'views/claim_sequence.xml',
        'views/crm_claim_menu.xml',
        'views/crm_claim_data.xml',
        'views/res_partner_view.xml',
        'views/crm_claim_line_view.xml',
        'views/crm_team_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    "images":["static/description/Banner.png"],
}
