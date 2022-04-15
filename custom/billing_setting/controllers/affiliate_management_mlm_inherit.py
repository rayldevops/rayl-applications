#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>;
#################################################################################
from odoo import http, _
from odoo.http import request
import werkzeug
import logging

_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from odoo.addons.affiliate_management_mlm.controllers.main import WebsiteAffiliateMLM
import stripe
from odoo.exceptions import ValidationError


class WebsiteAffiliateMLMInherit(WebsiteAffiliateMLM):

    @http.route('/affiliate/mlm-product-upgrade', auth='user', type='http', website=True)
    def mlm_upgrade_membership_sol(self, **kw):

        sale_order_id = request.website.sale_get_order()
        product_id = request.website.get_mlm_upgrade_product()
        stripe_data = request.env['payment.acquirer'].sudo().search([('state', '=', 'enabled'),
                                                                     ('provider', '=', 'stripe')])

        if not request.env.user.partner_id.bought_membership and request.env.user.partner_id.upgrade_membership:
            raise UserError('You need to buy rayl affiliate to buy pro')

        if not sale_order_id:
            sale_order_id = request.website.sale_get_order(force_create=True)

        if len(request.env["sale.order.line"].sudo().search(["&", ("order_id", "=", sale_order_id.id), (
                "product_id", "=", product_id.product_variant_id.id)])) == 0:
            vals = {
                "product_id": product_id.product_variant_id.id,
                "order_id": sale_order_id.id
            }

        order_line = request.env['sale.order.line'].sudo().create(vals)

        val = {'acquirer_id': stripe_data.id,
               'return_url': '/shop/payment/validate'}

        transaction = sale_order_id._create_payment_transaction(val)
        old_subscription_id = order_line.order_partner_id.stripe_subscription_id
        request.session['sale_last_order_id'] = sale_order_id.id
        if old_subscription_id and transaction:
            try:
                stripe.api_key = stripe_data.stripe_secret_key
                subscription = stripe.Subscription.retrieve(old_subscription_id)
                if subscription:
                    res_sub = stripe.Subscription.modify(
                        old_subscription_id,
                        proration_behavior='always_invoice',
                        items=[
                            {
                                "id": subscription['items']['data'][0].id,
                                "price": order_line.product_id.stripe_plan_id
                            },
                        ],
                        expand=['latest_invoice']
                    )
                    if res_sub:
                        checkout_object = res_sub['items']['data'][0]
                        if checkout_object['subscription']:
                            transaction.sudo().write({
                                'stripe_subscription_id': checkout_object['subscription']
                            })
                            order_line.order_id.action_confirm()
                            return request.redirect("/shop/confirmation")


            except stripe.error.CardError as e:
                # Since it's a decline, stripe.error.CardError will be caught
                raise UserError(e)
            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                raise UserError(e)
            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                raise UserError(e)
            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                raise UserError(e)
            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                raise UserError(e.user_message)
            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                raise UserError(e)
            except Exception as e:
                # Something else happened, completely unrelated to Stripe
                raise UserError(e)
        else:
            return request.redirect("/affiliate/upgrade_membership?error=You need to buy Ambassador Program to buy pro")

    @http.route('/affiliate/upgrade_membership', methods=['GET', 'POST'], auth='public', type='http', website=True)
    def mlm_upgrade_membership(self, **kw):

        error = dict()
        error_message = []
        errors = {}
        if kw.get('error'):
            error_message.append(_(kw.get('error')))

        message = dict()
        success_message = []
        messages = {}
        if kw.get('message'):
            success_message.append(_(kw.get('message')))

        product = request.website.get_mlm_upgrade_product()
        mlm_config = request.env['affiliate.program'].sudo().get_mlm_configuration()

        errors['error_message'] = error_message
        messages['success_message'] = success_message

        values = {
            "product_temp_id": product,
            "mlm_work_title": mlm_config.get('mlm_work_title'),
            "mlm_work_text": mlm_config.get('mlm_work_text'),
            'error': errors,
            'message': messages,
        }

        return http.request.render('affiliate_management_mlm.mlm_upgrade_membership', values)
