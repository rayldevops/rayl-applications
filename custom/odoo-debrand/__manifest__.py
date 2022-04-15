{
    'name': "Odoo Debranding",
    'version': "14.0.1.0.0",
    'summary': """Odoo Backend and Front end Debranding""",
    'description': """Debrand Odoo,Debranding, odoo14""",
    'author': "Planet Odoo",
    'company': "Planet Odoo",
    'maintainer': "Planet Odoo",
    'website': "https://planet-odoo.in/",
    'category': 'Tools',
    'depends': ['website', 'base_setup'],
    'data': [
        'views/views.xml',
        'views/res_config_views.xml',
        'views/ir_module_views.xml'
    ],
    'qweb': ["static/src/xml/base.xml",
             "static/src/xml/res_config_edition.xml"],
    'images': ['static/description/planetodoo.png'],
    'installable': True,
    'application': False
}
