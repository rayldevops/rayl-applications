# -*- coding: utf-8 -*-
import json
import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request
from odoo.addons.payment_stripe.controllers.main import StripeController

_logger = logging.getLogger(__name__)


class StripeInherit(StripeController):
    _success_url = '/payment/stripe/success'
    _cancel_url = '/payment/stripe/cancel'

    @http.route(['/payment/stripe/success'], type='http', auth='public')
    def stripe_success(self, **kwargs):
        # request.env['payment.transaction'].sudo().form_feedback(kwargs, 'stripe')
         return werkzeug.utils.redirect('/payment/process')

    # @http.route(['/payment/stripe/old_paid_subscription'], type='http', auth='public')
    # def old_paid_subscription(self, **kwargs):
    #     old_transaction = request.env['payment.transaction'].sudo().search([('state', '=', 'done')])
    #     for transaction in old_transaction:
    #         if not transaction.stripe_subscription_id:
    #
    #     return "True"