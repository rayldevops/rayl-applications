{
    "name": "Webiste Terms And Conditions",
    "summary": "Show Terms And Conditions In Website Before Sign Up And Process Chekout.",
    "category": "Webiste Terms And Conditions",
    "version": "14.0.4",
    "sequence": 1,
    "depends": [
        'base','auth_signup',
        'web','website_sale','website_mail',],
    "data": [
        'views/templates.xml',
        'views/report.xml',
    ],
    "qweb": [
        # 'static/src/xml/website.xml',
    ],
    "images": [],
    "application": False,
    "installable": True,
}
