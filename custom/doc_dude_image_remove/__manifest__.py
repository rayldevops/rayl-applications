{
    'name': "Odoo Doc Dude Removal",
    'version': "14.0.1.0.0",
    'summary': """Odoo Doc Dude Removal Debranding""",
    'description': """Debrand Odoo14""",
    'author': "Planet Odoo",
    'company': "Planet Odoo",
    'maintainer': "Planet Odoo",
    'website': "https://planet-odoo.in/",
    'category': 'Tools',
    'depends': ['website','project','account','base_automation','account_test','hr_holidays',
                'survey','maintenance','base_setup','base','crm','hr_expense','purchase','mail','stock'],
    'data': [
        'views/doc_dude_remove.xml'
    ],
    'qweb': [],
    'images': [],
    'installable': True,
    'application': False
}
