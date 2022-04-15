# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        user_id = http.request.env.context.get('uid')
        if 'billing_details_count' in counters:
            values['billing_details_count'] = request.env['billing.setting'].search_count([('user_id', '=', user_id)])
        if 'payout_details_count' in counters:
            values['payout_details_count'] = request.env['payout.setting'].search_count([('user_id', '=', user_id)])
        return values
