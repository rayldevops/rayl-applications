{
    "name": "Paypal subscription Customization",
    "summary": "Added paypal button on website product for subscription.",
    "version": "14.0.1",
    "sequence": 1,
    "depends": [
        'base','auth_signup','web','website_sale','product'],
    "data": [
        'views/templates.xml',
    ],
    "qweb": [
        # 'static/src/xml/website.xml',
    ],
    "images": [],
    "application": False,
    "installable": True,
}
