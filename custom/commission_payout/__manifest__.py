{
    "name": "Commission Payout",
    "summary": "Commission Payout.",
    "category": "Commission Payout",
    "version": "14.0.4",
    "sequence": 1,
    "depends": [
        'base','auth_signup',
        'web','website_sale','portal','affiliate_management',],
    "data": [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/commission.xml',
    ],
    "qweb": [

    ],
    "images": [],
    "application": False,
    "installable": True,
}
