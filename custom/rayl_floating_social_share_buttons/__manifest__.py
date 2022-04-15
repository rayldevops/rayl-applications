# -*- coding: utf-8 -*-
# Copyright 2019 GTICA.C.A. - Ing Henry Vivas

{
    'name': 'Rayl Social Share Buttons',
    'summary': 'You can display share buttons on social media on your website using the sidebar.',
    'category': 'Website/Website',
    'version': '13.0.1.0.0',
    'sequence': 100,
    'license': 'OPL-1',
    'website': 'https://www.rayl.com',
    'price': 21.00,
    'currency': 'EUR',
    'description': "",
    'depends': ['website'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/view_share_buttons_list.xml',
        'views/res_config_settings.xml',
        'views/rayl_floating_social_share_buttons_assets.xml',
        'views/rayl_floating_social_share_buttons_templates.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'qweb': [
        'static/src/xml/website_share_buttons.xml'
    ],
    'images': ['static/description/main_screenshot.gif'],
    'installable': True,
    'application': False,
} 
