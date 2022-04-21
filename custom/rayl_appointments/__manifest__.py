# -*- coding: utf-8 -*-
{
    'name': "Website Appointment Booking in Rayl, calendar slot booking in Rayl",
    'summary': "Website Appointment Booking in Rayl,Website Booking in Rayl",
    'description': """
       Website Appointment Booking in Rayl Website Booking, slot booking consultant booking online booking book appointment """,
    'category': 'website',
    'version': '14.0.1.2.0',
    # any module necessary for this one to work correctly
    'depends': ['base','calendar','account','crm','contacts',
                'website','website_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/website_calendar_data.xml',
        'views/assets.xml',
        'views/portal_templates_view.xml',
        'views/portal_appointment_templates.xml',
        'views/appointment_views.xml',
        'views/menu_dashboard_view.xml',
        'views/website.xml',
        'views/website_view.xml',
        'views/appointment_source_views.xml',
        'views/appointee_views.xml',
        'views/appointment_group_views.xml',
        'views/appointment_timeslot_views.xml',
        'views/calendar_appointment_views.xml',
    ],
    'qweb': ["static/src/xml/appointment_dashboard.xml",
             ],

    'price': 165.00,
    'currency': 'USD',
    'support': 'business@axistechnolabs.com',
    'author': 'Rayl',
    # 'website': 'https://www.axistechnolabs.com',
    'installable': True,
    'license': 'OPL-1',
    'images': ['static/description/images/banner.jpg'],

}
