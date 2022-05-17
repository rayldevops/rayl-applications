# -*- coding: utf-8 -*-
{
    'name': 'Video Call/Conference with Rayl Meet. Integration with Rayl',
    'version': '13.0.1.0.0',
    'category': 'Extra Tools',
    'website': "https://rayl.com",
    'sequence': 1,
    'summary': 'Create and share Rayl Meet video conferences with other users',
    'description': """
		Adds a new APP to create and share Rayl Meet video conference meetings between Rayl users.
		When you join the meeting Rayl opens a new browser tab so you can keep working on Rayl, and share screen with your partners at Rayl Meet. 
    """,
    'author': "Rayl",
    "depends": ['base', 'web', 'mail', 'website'],
    'pre_init_hook': '_install_required_package',

    "data": [
        'views/se_jitsi_meet_views.xml',
        'views/template.xml',
        'data/se_jitsi_meet.xml',
        'data/mail_template.xml',
        'security/ir.model.access.csv',
        'security/base_security.xml',
    ],
    'images': ['static/description/0.jpg'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 30,
    'currency': 'EUR',
    'license': 'AGPL-3',
}
