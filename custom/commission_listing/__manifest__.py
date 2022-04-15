{
    "name": "Commission Listing",
    "summary": "Commission Listing",
    "category": "Commission Listing",
    "version": "14.0.4",
    "external_dependencies": {"python": ["xlsxwriter","xlrd"]},
    "sequence": 1,
    "depends": [
        'base', 'auth_signup',
        'web', 'website_sale', 'portal', 'affiliate_management'],
    "data": [
        # 'security/ir.model.access.csv',
        'views/commission.xml',
        'views/templates.xml',
    ],
    "qweb": [

    ],
    "images": [],
    "application": False,
    "installable": True,
}
