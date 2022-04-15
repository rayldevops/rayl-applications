# -*- coding: utf-8 -*-
{
    'name': 'RAYL Customization',
    'version': '14.0.1.0.0',
    'category': 'Tools',
    'website': "https://planet-odoo.com",
    'sequence': 1,
    'summary': 'RAYL customization',
    'description': """
		All the customization for rayl saas instances. 
    """,
    'author': "Planet odoo",
    "depends": ['base', 'auth_signup', 'web', 'mail', 'product','microsoft_calendar', 'google_calendar'],
    "data": [
        'security/rayl_security.xml',
        'security/ir.model.access.csv',
        'views/setting_view.xml',
    ],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
