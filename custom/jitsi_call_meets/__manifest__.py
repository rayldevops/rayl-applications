{
    "name": "Jitsi Call Meets",
    "summary": "Craete and join meeting by click on call button.",
    "category": "Jitsi Call Meeting",
    "version": "1.0.4",
    "sequence": 1,
    "website": "http://www.webkul.com",
    # "live_test_url"        :  "http://odoodemo.webkul.com/?module=jitsi_call_meets",
    "depends": [
        'base',
        'web',
        'mail',
        'se_jitsi_meet',
    ],
    "data": [
        'wizard/invite_user_wizard.xml',
        'views/templates.xml',
    ],
    "qweb": [
        'static/src/xml/themeslider.xml',
    ],
    "images": [],
    "application": False,
    "installable": True,
    # "price"                :  99,
    # "currency"             :  "EUR" ,
    # "pre_init_hook"        :  "pre_init_check",

}
