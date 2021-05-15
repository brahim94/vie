# -*- coding: utf-8 -*-
{
    'name': "tech_accesright",

    'summary': """TECH-IT MAROC""",

    'description': """
        Long description of module's purpose
    """,

    'author': "TECH-IT",
    'website': "http://www.tech-it.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'bi_crm_claim', 'mass_mailing', 'wt_helpdesk'],

    # always loaded
    'data': [
        'security/security_sav.xml',
        'security/security_reclamation.xml',
        #'security/ir.model.access.csv',
        #'views/views.xml',
        #'views/templates.xml',
        'views/acces_right.xml',
        
    ],
    # only loaded in demonstration mode
    #'demo': [
    #    'demo/demo.xml',
    #],
}
