# coding: utf-8

from collections import namedtuple
from datetime import datetime
from hashlib import sha256
import hmac
import json
import logging
import requests
import pprint
from requests.exceptions import HTTPError
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.http import request
from odoo.tools.float_utils import float_round
from odoo.tools import consteq
from odoo.exceptions import ValidationError

from odoo.addons.payment_stripe.controllers.main import StripeController

_logger = logging.getLogger(__name__)

# The following currencies are integer only, see https://stripe.com/docs/currencies#zero-decimal
INT_CURRENCIES = [
    u'BIF', u'XAF', u'XPF', u'CLP', u'KMF', u'DJF', u'GNF', u'JPY', u'MGA', u'PYG', u'RWF', u'KRW',
    u'VUV', u'VND', u'XOF'
]
STRIPE_SIGNATURE_AGE_TOLERANCE = 600  # in seconds


class PaymentAcquirerStripe(models.Model):
    _inherit = 'payment.acquirer'

    def stripe_form_generate_values(self, tx_values):
        self.ensure_one()
        tx_values
        base_url = self.get_base_url()

        stripe_session_data = {
            'line_items[][price]': tx_values['partner'].last_website_so_id.order_line.product_id.stripe_plan_id,
            'line_items[][quantity]': 1,
            'client_reference_id': tx_values['reference'],
            'success_url': urls.url_join(base_url, StripeController._success_url) + '?reference=%s' % tx_values[
                'reference'],
            'cancel_url': urls.url_join(base_url, StripeController._cancel_url) + '?reference=%s' % tx_values[
                'reference'],
            'mode': 'subscription',
        }
        if tx_values['partner'].stripe_customer_id:
            stripe_session_data['customer'] = tx_values['partner'].stripe_customer_id
        else:
            stripe_session_data['customer_email'] = tx_values.get('partner_email') or tx_values.get(
                'billing_partner_email')

        self._add_available_payment_method_types(stripe_session_data, tx_values)

        tx_values['session_id'] = self.with_context(stripe_manual_payment=True)._create_stripe_session(
            stripe_session_data)

        return tx_values

    def _handle_checkout_webhook_complete(self, checkout_object: dir):
        """
        Process a checkout.session.completed Stripe web hook event,
        mark related payment successful

        :param checkout_object: provided in the request body
        :return: True if and only if handling went well, False otherwise
        :raises ValidationError: if input isn't usable
        """
        tx_reference = checkout_object.get('client_reference_id')
        stripe_subscription_id = checkout_object.get('subscription')
        stripe_customer_id = checkout_object.get('customer')
        _logger.info(tx_reference)
        _logger.info(stripe_subscription_id)
        _logger.info(stripe_customer_id)
        data = {'reference': tx_reference}
        # data = {'reference': 'S00277-1'}
        try:
            odoo_tx = self.env['payment.transaction'].sudo()._stripe_form_get_tx_from_data(data)
            _logger.info('odoo_tx paid Search %s', odoo_tx)
            odoo_tx.stripe_subscription_id = stripe_subscription_id
            # odoo_tx.partner_id.id.stripe_subscription_id = stripe_subscription_id
        except ValidationError as e:
            _logger.info('Received notification for tx %s. Skipped it because of %s', tx_reference, e)
            return False
        _logger.info(odoo_tx)
        try:
            res_part = self.env['res.partner'].sudo().search([('id', '=', odoo_tx.partner_id.id)])
            _logger.info('res_part Search %s', res_part)
            res_part.sudo().write({
                'stripe_customer_id': stripe_customer_id,
                'stripe_subscription_id': stripe_subscription_id,
            })
        except ValidationError as e:
            _logger.info('Received notification for tx %s. Skipped it because of %s', tx_reference, e)
            return False
        _logger.info(res_part)
        PaymentAcquirerStripe._verify_stripe_signature(odoo_tx.acquirer_id)

        _logger.info(data)
        _logger.info('Updated Subscription %s', stripe_subscription_id)
        return True

    def _handle_checkout_webhook_paid(self, checkout_object: dir):
        """
        Process a checkout.session.completed Stripe web hook event,
        mark related payment successful

        :param checkout_object: provided in the request body
        :return: True if and only if handling went well, False otherwise
        :raises ValidationError: if input isn't usable
        """
        stripe_subscription_id = checkout_object.get('subscription')
        stripe_payment_intent = checkout_object.get('payment_intent')
        stripe_customer_id = checkout_object.get('customer')
        billing_reason = checkout_object.get('billing_reason')
        _logger.info(stripe_subscription_id)
        _logger.info(stripe_payment_intent)
        _logger.info(stripe_customer_id)
        data = {'stripe_subscription_id': stripe_subscription_id}
        # data = {'stripe_subscription_id': 'sub_Jtqyj2FwOIISV9'}
        try:
            odoo_tx = self.env['payment.transaction'].sudo()._stripe_form_get_tx_from_data_subscription(data)
            _logger.info('odoo_tx paid Search %s', odoo_tx)
            # if odoo_tx:
            #     odoo_ux = self.env['payment.transaction'].sudo().search([('stripe_subscription_id', '=', stripe_subscription_id), ('stripe_payment_intent', '=', '')])
            #     _logger.info('Odoo_ux paid Search %s', odoo_ux)
            #     odoo_ux.write({
            #         'stripe_payment_intent': stripe_payment_intent,
            #     })
            odoo_tx.stripe_payment_intent = stripe_payment_intent
            data.update({'reference': odoo_tx.reference})
        except ValidationError as e:
            _logger.info('Received notification for tx %s. Skipped it because of %s', stripe_subscription_id, e)
            return False
        _logger.info(odoo_tx)
        _logger.info("PaymentAcquirerStripe")
        try:
            res_part = self.env['res.partner'].sudo().search([('id', '=', odoo_tx.partner_id.id)])
            _logger.info('res_part Search %s', res_part)
            start_date = datetime.fromtimestamp(
                checkout_object.get('lines').get('data')[0]['period']['start']).strftime('%Y-%m-%d')
            end_date = datetime.fromtimestamp(checkout_object.get('lines').get('data')[0]['period']['end']).strftime(
                '%Y-%m-%d')
            if 'Unused time' in checkout_object.get('lines').get('data')[0]['description']:
                stripe_subscription_plan_description = '1 × Ambassador Bundle Program (CAD) (at $59.95 / month) by Upgrade'
            else:
                stripe_subscription_plan_description = checkout_object.get('lines').get('data')[0]['description']
            res_part.sudo().write({
                'stripe_subscription_start_date': start_date,
                'stripe_subscription_end_date': end_date,
                'stripe_subscription_plan_description': stripe_subscription_plan_description,
            })
        except ValidationError as e:
            _logger.info('Received notification for tx %s. Skipped it because of %s', res_part, e)
            return False
        _logger.info(res_part)

        if billing_reason != 'subscription_cycle':
            PaymentAcquirerStripe._verify_stripe_signature(odoo_tx.acquirer_id)

        _logger.info("PaymentAcquirerStripe2")
        url = 'payment_intents/%s' % stripe_payment_intent
        stripe_tx = odoo_tx.acquirer_id._stripe_request(url)

        _logger.info(url)
        _logger.info(stripe_tx)

        if 'error' in stripe_tx:
            error = stripe_tx['error']
            raise ValidationError("Could not fetch Stripe payment intent related to %s because of %s; see %s" % (
                odoo_tx, error['message'], error['doc_url']))

        if stripe_tx.get('charges') and stripe_tx.get('charges').get('total_count'):
            charge = stripe_tx.get('charges').get('data')[0]
            _logger.info("Got data", data)
            _logger.info("Got Charges", charge)
            data.update(charge)

        _logger.info(data)

        if billing_reason != 'subscription_cycle':
            odoo_tx.form_feedback(data, 'stripe')

        subscription_invoice = self.env['sale.subscription'].sudo().search([('partner_id', '=', odoo_tx.partner_id.id)],
                                                                           limit=1)
        if subscription_invoice and subscription_invoice.payment_gateway_sub_id == False and subscription_invoice.payment_gateway_sub_id != stripe_subscription_id:
            subscription_invoice.payment_gateway_sub_id = stripe_subscription_id
        elif not subscription_invoice:
            odoo_tx.sale_order_ids.update_existing_subscriptions()
            odoo_tx.sale_order_ids.create_subscriptions()
            subscription_invoice = self.env['sale.subscription'].sudo().search(
                [('partner_id', '=', odoo_tx.partner_id.id)],
                limit=1)
            old_invoice_object = self.env['account.move'].search(
                [('partner_id', '=', odoo_tx.partner_id.id),('invoice_line_ids.subscription_id','=',False),
                 ('move_type', '=', 'out_invoice')])
            if old_invoice_object:
                for inv in old_invoice_object:
                    inv.invoice_line_ids.subscription_id = subscription_invoice.id
            subscription_invoice.payment_gateway_sub_id = stripe_subscription_id
        if billing_reason == 'subscription_cycle':
            if subscription_invoice:
                invoice_obj = self.env['account.move'].search(
                    [('invoice_line_ids.subscription_id', '=', subscription_invoice.id), ('state', '=', 'draft')], limit=1)
                if not invoice_obj:
                    subscription_invoice.generate_recurring_invoice()
            invoice_draft = self.env['account.move'].search(
                [('partner_id', '=', odoo_tx.partner_id.id), ('state', '=', 'draft')], limit=1)
            if invoice_draft:
                if not invoice_draft.payment_gateway_reference and invoice_draft.payment_gateway_reference != stripe_payment_intent:
                    invoice_draft.payment_gateway_reference = stripe_payment_intent
                    invoice_draft._post(False)
                    journal_id_stripe = self.env['account.journal'].sudo().search([('code', '=', 'STRIP')], limit=1).id
                    pmt_wizard = self.env['account.payment.register'].with_context(active_model='account.move',
                                                                                   active_ids=invoice_draft.ids).create(
                        {
                            'journal_id': journal_id_stripe,
                        })
                    pmt_wizard._create_payments()
                    line_id = 0
                    line_product_id = 0
                    for line in odoo_tx.sale_order_ids.order_line:
                        line_id = line.id
                        line_product_id = line.product_id.id
                    affiliate_visit = self.env['affiliate.visit']
                    visit = affiliate_visit.create({
                        'affiliate_method': 'pps',
                        'affiliate_key': odoo_tx.partner_id.res_affiliate_key,
                        'parent_affiliate_partner_id': odoo_tx.partner_id.parent_aff.id,
                        'affiliate_partner_id': odoo_tx.partner_id.id,
                        'url': "",
                        'affiliate_type': 'product',
                        'type_name': line_product_id,
                        'sales_order_line_id': line_id,
                        'convert_date': fields.datetime.now(),
                        'affiliate_program_id': odoo_tx.partner_id.affiliate_program_id.id,
                        'product_quantity': '1',
                        'commission_amt': odoo_tx.partner_id.affiliate_program_id.amount,
                        'tier1': True,
                        'is_converted': True
                    })
                    # odoo_tx._do_payment(stripe_payment_intent, invoice, two_steps_sec=False)[0]
                _logger.info(invoice_draft)
        return True

    def _handle_stripe_webhook(self, data):
        """Process a webhook payload from Stripe.

        Post-process a webhook payload to act upon the matching payment.transaction
        record in Odoo.
        """
        stripe_object = data.get('data', {}).get('object')
        if not stripe_object:
            raise ValidationError('Stripe Webhook data does not conform to the expected API.')
        else:
            wh_type = data.get('type')
            if wh_type == 'checkout.session.completed':
                # Payment is successful and the subscription is created.
                # You should provision the subscription and save the customer ID to your database.
                _logger.info('handling %s webhook event from stripe', wh_type)
                return self._handle_checkout_webhook_complete(stripe_object)
            elif wh_type == 'invoice.paid':
                # Continue to provision the subscription as payments continue to be made.
                # Store the status in your database and check when a user accesses your service.
                # This approach helps you avoid hitting rate limits.
                _logger.info('handling %s webhook event from stripe', wh_type)
                return self._handle_checkout_webhook_paid(stripe_object)
            elif wh_type == 'invoice.payment_failed':
                # The payment failed or the customer does not have a valid payment method.
                # The subscription becomes past_due. Notify your customer and send them to the
                # customer portal to update their payment information.
                raise ValidationError('The payment failed or the customer does not have a valid payment method.')
            else:
                _logger.info('unsupported webhook type %s, ignored', wh_type)
                return False
        return False

    def _verify_stripe_signature(self):
        """
        :return: true if and only if signature matches hash of payload calculated with secret
        :raises ValidationError: if signature doesn't match
        """
        _logger.info('handling %s webhook event from self', self)
        if not self.stripe_webhook_secret:
            raise ValidationError('webhook event received but webhook secret is not configured')
        signature = request.httprequest.headers.get('Stripe-Signature')
        body = request.httprequest.data

        sign_data = {k: v for (k, v) in [s.split('=') for s in signature.split(',')]}
        event_timestamp = int(sign_data['t'])
        if datetime.utcnow().timestamp() - event_timestamp > STRIPE_SIGNATURE_AGE_TOLERANCE:
            _logger.error('stripe event is too old, event is discarded')
            raise ValidationError('event timestamp older than tolerance')

        signed_payload = "%s.%s" % (event_timestamp, body.decode('utf-8'))

        actual_signature = sign_data['v1']
        expected_signature = hmac.new(self.stripe_webhook_secret.encode('utf-8'),
                                      signed_payload.encode('utf-8'),
                                      sha256).hexdigest()

        if not consteq(expected_signature, actual_signature):
            _logger.error(
                'incorrect webhook signature from Stripe, check if the webhook signature '
                'in Odoo matches to one in the Stripe dashboard')
            raise ValidationError('incorrect webhook signature')

        return True


class PaymentTransactionStripe(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _stripe_form_get_tx_from_data_subscription(self, data):
        """ Given a data dict coming from stripe, verify it and find the related
        transaction record. """
        stripe_subscription_id = data.get('stripe_subscription_id')
        if not stripe_subscription_id:
            stripe_error = data.get('error', {}).get('message', '')
            _logger.error('Stripe: invalid reply received from stripe API, looks like '
                          'the transaction failed. (error: %s)', stripe_error or 'n/a')
            error_msg = _("We're sorry to report that the transaction has failed.")
            if stripe_error:
                error_msg += " " + (_("Stripe gave us the following info about the problem: '%s'") %
                                    stripe_error)
            error_msg += " " + _("Perhaps the problem can be solved by double-checking your "
                                 "credit card details, or contacting your bank?")
            raise ValidationError(error_msg)
        _logger.error(self)
        tx = self.search([('stripe_subscription_id', '=', stripe_subscription_id)], order='id desc', limit=1)
        if not tx:
            error_msg = _('Stripe: no order found for reference %s', stripe_subscription_id)
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        elif len(tx) > 1:
            error_msg = _('Stripe: %(count)s orders found for reference %(reference)s', count=len(tx),
                          reference=stripe_subscription_id)
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return tx[0]

    def form_feedback_new(self, data, acquirer_name):
        if data.get('stripe_subscription_id') and acquirer_name == 'stripe':
            transaction = self.env['payment.transaction'].sudo().search(
                [('stripe_subscription_id', '=', data['stripe_subscription_id'])])
            _logger.info('transaction', transaction)
            url = 'payment_intents/%s' % transaction.stripe_payment_intent
            resp = transaction.acquirer_id._stripe_request(url)
            if resp.get('charges') and resp.get('charges').get('total_count'):
                resp = resp.get('charges').get('data')[0]
            data.update(resp)
            _logger.info('Stripe: entering form_feedback with post data %s' % pprint.pformat(data))
        return super(PaymentTransactionStripe, self).form_feedback(data, acquirer_name)
