{
    "name": "Login as another user in website",
    "version": "0.1",
    "author": "Planet Odoo",
    "license": 'AGPL-3',
    "category": "Tools",
    "description": """
==========================================
""",
    "depends": ['website'],
    "data": [
        "views/res_users_view.xml",
        "views/webclient_templates.xml",
    ],
    "demo": [],
    "qweb": [
        "static/src/xml/login_as.xml",
    ],
    "installable": True,
    "active": False,
}
