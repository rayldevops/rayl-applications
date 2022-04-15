{
    'name': "SaaS Automation",
    'version': "14.0.1.0.0",
    'summary': """This module will create saas contract and client instance""",
    'description': """Saas automation""",
    'author': "Planet Odoo",
    'company': "Planet Odoo",
    'maintainer': "Planet Odoo",
    'website': "https://planet-odoo.in/",
    'category': 'Tools',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/affiliate_saas_configuration.xml',
        'views/saas_partner.xml',
    ],
    'qweb': [],
    'images': [],
    'installable': True,
    'application': False
}
