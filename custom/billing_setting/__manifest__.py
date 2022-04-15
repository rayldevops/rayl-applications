{
    "name": "Billing Settings",
    "summary": "Billing Settings.",
    "category": "Billing Settings",
    "version": "14.0.4",
    "sequence": 1,
    "depends": [
        'base','auth_signup',
        'web','website_sale','portal','affiliate_management'],
    "data": [
        'security/ir.model.access.csv',
        'views/product_inherit.xml',
        'views/templates.xml',
        'views/billing.xml',
        'views/payout.xml',
        'views/product_inherit.xml',
    ],
    "qweb": [

    ],
    "images": [],
    "application": False,
    "installable": True,
}
