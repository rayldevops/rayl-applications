from odoo import fields, models, http, _
from odoo.http import request
from odoo.addons.base.models.ir_ui_view import keep_query
import odoo
import re
import werkzeug
from lxml import etree
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError, AccessDenied
import stripe


class BillingAccounts(http.Controller):

    @http.route(['/my/billing'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def my_billing(self, **kw):
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

        user_id = http.request.env.context.get('uid')
        value_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        values = value_user.partner_id
        if values.stripe_customer_id:
            bank_details = request.env['bank.details'].sudo().search([])
            errors['error_message'] = error_message
            messages['success_message'] = success_message
            return request.render("billing_setting.billing_setting_form", {'values': bank_details,
                                                                           'error': errors, 'message': messages})
        else:
            country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(
                int(values['country_id']))
            errors['error_message'] = error_message
            messages['success_message'] = success_message
            render_values = {
                'user_details': values,
                'country': country,
                'country_states': country.get_website_sale_states(mode="edit"),
                'countries': country.get_website_sale_countries(mode="edit"),
                'error': errors,
                'message': messages,
            }
            return request.render("billing_setting.user_details_form", render_values)

    @http.route(['/my/user_details'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def my_user_details(self, **kw):

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

        user_id = http.request.env.context.get('uid')
        value_user = request.env['res.users'].sudo().search([('id', '=', user_id)])

        values = value_user.partner_id
        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(
            int(values['country_id']))

        errors['error_message'] = error_message
        messages['success_message'] = success_message
        render_values = {
            'user_details': values,
            'country': country,
            'country_states': country.get_website_sale_states(mode="edit"),
            'countries': country.get_website_sale_countries(mode="edit"),
            'error': errors,
            'message': messages,
        }
        return request.render("billing_setting.user_details_form", render_values)

    @http.route('/my/bank/submit', type='http', auth="public", website=True)
    def billing_form_submit(self, *args, **post):
        digits_to_keep = 4
        mask_char = '#'
        masked_string = False
        masked_card_num = False
        if post:
            if post.get('payment_option') == 'electronic_funds_transfer':
                if post.get('bank_account_number') != post.get('confirm_bank_account_number'):
                    return request.redirect('/my/billing/?error=Bank Account Number do not match. Please retype them.')
                else:
                    acc_number = post.get('bank_account_number')
                    num_of_digits = sum(map(str.isdigit, acc_number))
                    digits_to_mask = num_of_digits - digits_to_keep
                    masked_string = re.sub('\d', mask_char, acc_number, digits_to_mask)
                    billing_obj = request.env['billing.setting'].sudo().create({
                        'payment_option': "electronic_funds_transfer",
                        'bank_id': post.get('bank_id'),
                        'branch_transit_number': post.get('branch_transit_number'),
                        'bank_account_number': post.get('bank_account_number'),
                        'mask_bank_account_number': masked_string,
                        'confirm_bank_account_number': post.get('confirm_bank_account_number'),
                    })
                    return werkzeug.utils.redirect("/my/billing/?message=Data Updated Successfully")
            else:
                return request.redirect('/my/billing/?error=Invalid Post Details')
        return request.redirect('/my/billing/?error=Failed to Add Bank Details')

    @http.route('/my/card/submit', type='http', auth="public", website=True)
    def card_form_submit(self, *args, **post):
        if post:
            if post.get('payment_option') == 'credit_card':
                user_id = http.request.env.context.get('uid')
                value_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
                stripe_data = request.env['payment.acquirer'].sudo().search([('state', '=', 'enabled'),
                                                                             ('provider', '=', 'stripe')])
                #stripe.api_key = stripe_data.stripe_secret_key
                stripe.api_key = "sk_test_51Iv8YkSJCK9vw4PcEgaM2nGzP4NjFNHWb0HtQaINat3hLL5v6fTE2DsfFntr6QoIQCjcfS9LRfYK1P8tYxOi1PPv00RweJrr7f"
                try:
                    res_token = stripe.Token.create(
                        card={
                            "number": post.get('card_number'),
                            "exp_month": post.get('exp_month'),
                            "exp_year": post.get('exp_year'),
                            "cvc": post.get('card_code'),
                        },
                    )
                    if hasattr(res_token, 'id'):
                        res_add_card = stripe.Customer.create_source(
                            value_user.partner_id.stripe_customer_id,
                            source=res_token['id'],
                        )
                        if hasattr(res_add_card, 'id'):
                            card_obj = request.env['billing.setting'].sudo().create({
                                'payment_option': post.get('payment_option'),
                                'stripe_card_id': res_add_card['id'],
                                'stripe_card_brand': res_add_card['brand'],
                                'stripe_card_customer': res_add_card['customer'],
                                'stripe_card_exp_month': res_add_card['exp_month'],
                                'stripe_card_exp_year': res_add_card['exp_year'],
                                'stripe_card_last4': res_add_card['last4'],
                                'stripe_card_fingerprint': res_add_card['fingerprint'],
                                'street_address': post.get('street_address'),
                                'post_code': post.get('post_code'),
                            })
                            if card_obj:
                                card_count = request.env['billing.setting'].sudo().search([('user_id', '=', user_id)])
                                billing_rec = request.env['default.account'].sudo().search([('user_id', '=', user_id)])
                                if len(card_count) == 1 and not billing_rec:
                                    default_obj = request.env['default.account'].sudo().create({
                                        'default_billing_id': card_obj.id
                                    })
                                elif len(card_count) == 1 and billing_rec:
                                    default_obj = request.env['default.account'].sudo().search(
                                        [('user_id', '=', user_id)]).write({'default_billing_id': card_obj.id})
                            return request.redirect('/billing/account/?message=Successfully Added Card')
                        else:
                            return request.redirect('/my/billing/?error=Failed to Add Card')
                    else:
                        return request.redirect('/my/billing/?error=Failed to Generate Stripe Card Token')
                except stripe.error.CardError as e:
                    # Since it's a decline, stripe.error.CardError will be caught
                    return request.redirect('/my/billing/?error=' + e.user_message)
                except stripe.error.RateLimitError as e:
                    # Too many requests made to the API too quickly
                    return request.redirect('/my/billing/?error=' + e.user_message)
                except stripe.error.InvalidRequestError as e:
                    # Invalid parameters were supplied to Stripe's API
                    return request.redirect("/my/billing/?error=" + e.user_message)
                except stripe.error.AuthenticationError as e:
                    # Authentication with Stripe's API failed
                    # (maybe you changed API keys recently)
                    return request.redirect("/my/billing/?error=" + e.user_message)
                except stripe.error.APIConnectionError as e:
                    # Network communication with Stripe failed
                    return request.redirect('/my/billing/?error=' + e.user_message)
                except stripe.error.StripeError as e:
                    # Display a very generic error to the user, and maybe send
                    # yourself an email
                    return request.redirect('/my/billing/?error=' + e.user_message)
                except Exception as e:
                    # Something else happened, completely unrelated to Stripe
                    return request.redirect('/my/billing/?error=' + e)
        else:
            return request.redirect('/my/billing/?error=Please Check your Details and Try again')

    @http.route(['/my/user_details/submit'], type='http', auth="public", website=True)
    def user_details_submit(self, **post):
        if post:
            stripe_data = request.env['payment.acquirer'].sudo().search([('state', '=', 'enabled'),
                                                                         ('provider', '=', 'stripe')])
            stripe.api_key = stripe_data.stripe_secret_key
            # stripe.api_key = "sk_test_51Iv8YkSJCK9vw4PcEgaM2nGzP4NjFNHWb0HtQaINat3hLL5v6fTE2DsfFntr6QoIQCjcfS9LRfYK1P8tYxOi1PPv00RweJrr7f"
            user_id = http.request.env.context.get('uid')
            value_user = request.env['res.users'].sudo().search([('id', '=', user_id)])
            values = value_user.partner_id
            try:
                if values.stripe_customer_id:
                    res = stripe.Customer.modify(
                        values.stripe_customer_id,
                        address={
                            "line1": post.get('address'),
                            "city": post.get('city'),
                            "postal_code": post.get('postal_code'),
                            "state": value_user.state_id.display_name,
                        },
                        email=value_user.email,
                        name=value_user.name,
                    )
                else:
                    res = stripe.Customer.create(
                        address={
                            "line1": post.get('address'),
                            "city": post.get('city'),
                            "postal_code": post.get('postal_code'),
                            "state": value_user.state_id.display_name,
                        },
                        email=value_user.email,
                        name=value_user.name,
                    )
                if res:
                    billing_info = request.env['res.partner'].sudo().search(
                        [('id', '=', value_user.partner_id.id)]).write({
                        'street': post.get('address'),
                        'city': post.get('city'),
                        'country_id': post.get('country_id'),
                        'zip': post.get('postal_code'),
                        'state_id': post.get('state_id'),
                        'stripe_customer_id': res['id']
                    })
                    return request.redirect('/billing/account/?message=Data Updated Successfully')
                else:
                    return request.redirect('/my/user_details/?error=Failed To Update Details')
            except stripe.error.CardError as e:
                # Since it's a decline, stripe.error.CardError will be caught
                return request.redirect('/my/user_details/?error=' + e.user_message)
            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                return request.redirect('/my/user_details/?error=' + e.user_message)
            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                e
                return request.redirect("/my/user_details/?error=" + e.user_message)
            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                return request.redirect("/my/user_details/?error=" + e.user_message)
            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                return request.redirect('/my/user_details/?error=' + e.user_message)
            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                return request.redirect('/my/user_details/?error=' + e.user_message)
            except Exception as e:
                # Something else happened, completely unrelated to Stripe
                return request.redirect('/my/user_details/?error=' + e.user_message)
        else:
            return request.redirect('/my/user_details/?error=Please Check your Details and Try again')

    @http.route(['/billing/account'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def my_billing_account(self, **kw):
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

        user_id = http.request.env.context.get('uid')
        billing_details_eft = request.env['billing.setting'].sudo().search(
            [('user_id', '=', user_id), ('payment_option', '=', 'electronic_funds_transfer')])
        billing_details_cc = request.env['billing.setting'].sudo().search(
            [('user_id', '=', user_id), ('payment_option', '=', 'credit_card')])
        billing_details_count = request.env['billing.setting'].sudo().search_count([('user_id', '=', user_id)])
        billing_heading = request.env['sale.order'].sudo().search([('user_id', '=', user_id)], order='id desc', limit=1)

        errors['error_message'] = error_message
        messages['success_message'] = success_message

        return request.render("billing_setting.billing_account_list", {
            'billing_details_eft': billing_details_eft,
            'billing_details_cc': billing_details_cc,
            'billing_details_count': billing_details_count,
            'billing_heading': billing_heading,
            'error': errors,
            'message': messages,
        })

    @http.route('/set_default/billing/card', type='http', auth="public", website=True)
    def set_default_billing_card(self, **post):
        if post:
            billing_id = post.get('billing_setting_id')
            card_details = request.env['billing.setting'].sudo().search([('id', '=', billing_id)])
            partner_details = card_details.user_id.partner_id
            stripe_data = request.env['payment.acquirer'].sudo().search([('state', '=', 'enabled'),
                                                                         ('provider', '=', 'stripe')])
            stripe.api_key = stripe_data.stripe_secret_key
            # stripe.api_key = "sk_test_51Iv8YkSJCK9vw4PcEgaM2nGzP4NjFNHWb0HtQaINat3hLL5v6fTE2DsfFntr6QoIQCjcfS9LRfYK1P8tYxOi1PPv00RweJrr7f"
            try:
                update_default = stripe.Customer.modify(
                    partner_details.stripe_customer_id,
                    default_source=card_details.stripe_card_id,
                )
                if update_default:
                    user_id = http.request.env.context.get('uid')
                    billing_rec = request.env['default.account'].sudo().search([('user_id', '=', user_id)])
                    if billing_rec:
                        default_obj = request.env['default.account'].sudo().search([('user_id', '=', user_id)]).write({
                            'default_billing_id': billing_id,
                        })
                    else:
                        default_obj = request.env['default.account'].sudo().create({
                            'default_billing_id': billing_id,
                        })
                    return werkzeug.utils.redirect("/billing/account/?message=Data Updated Successfully")
                else:
                    return request.redirect('/billing/account/?error=Failed To Update Details')
            except stripe.error.CardError as e:
                # Since it's a decline, stripe.error.CardError will be caught
                return request.redirect('/billing/account/?error=' + e.user_message)
            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                return request.redirect('/billing/account/?error=' + e.user_message)
            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                return request.redirect("/billing/account/?error=" + e.user_message)
            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                return request.redirect("/billing/account/?error=" + e.user_message)
            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                return request.redirect('/billing/account/?error=' + e.user_message)
            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                return request.redirect('/billing/account/?error=' + e.user_message)
            except Exception as e:
                # Something else happened, completely unrelated to Stripe
                return request.redirect('/billing/account/?error=' + e.user_message)
        else:
            return request.redirect('/billing/account/?error=Please Check your Details and Try again')

    @http.route('/set_default/billing/bank', type='http', auth="public", website=True)
    def set_default_billing_bank(self, **post):
        user_id = http.request.env.context.get('uid')
        billing_id = post.get('billing_setting_id')
        billing_rec = request.env['default.account'].sudo().search([('user_id', '=', user_id)])
        if billing_rec:
            default_obj = request.env['default.account'].sudo().search([('user_id', '=', user_id)]).write({
                'default_billing_id': billing_id,
            })
        else:
            default_obj = request.env['default.account'].sudo().create({
                'default_billing_id': billing_id,
            })
        return werkzeug.utils.redirect("/billing/account?message=Data Updated Successfully")

    @http.route('/remove/billing/card', type='http', auth="public", website=True)
    def remove_billing_card(self, **post):
        billing_id = post.get('billing_setting_id')
        billing_obj = request.env['billing.setting'].sudo().search([('id', '=', billing_id)])
        partner_details = billing_obj.user_id.partner_id
        stripe_data = request.env['payment.acquirer'].sudo().search([('state', '=', 'enabled'),
                                                                     ('provider', '=', 'stripe')])
        stripe.api_key = stripe_data.stripe_secret_key
        # stripe.api_key = "sk_test_51Iv8YkSJCK9vw4PcEgaM2nGzP4NjFNHWb0HtQaINat3hLL5v6fTE2DsfFntr6QoIQCjcfS9LRfYK1P8tYxOi1PPv00RweJrr7f"
        try:
            remove_from_strip = stripe.Customer.delete_source(
                partner_details.stripe_customer_id,
                billing_obj.stripe_card_id,
            )
            if remove_from_strip:
                billing_obj.unlink()
                return werkzeug.utils.redirect("/billing/account/?message=Data Updated Successfully")
            else:
                return request.redirect('/billing/account/?error=Failed To Update Details')
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            return request.redirect('/billing/account/?error=' + e.user_message)
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            return request.redirect('/billing/account/?error=' + e.user_message)
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            return request.redirect("/billing/account/?error=" + e.user_message)
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            return request.redirect("/billing/account/?error=" + e.user_message)
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            return request.redirect('/billing/account/?error=' + e.user_message)
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            return request.redirect('/billing/account/?error=' + e.user_message)
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            return request.redirect('/billing/account/?error=' + e.user_message)

    @http.route('/remove/billing/bank', type='http', auth="public", website=True)
    def remove_billing_bank(self, **post):
        billing_id = post.get('billing_setting_id')
        billing_obj = request.env['billing.setting'].sudo().search([('id', '=', billing_id)])
        billing_obj.unlink()
        return werkzeug.utils.redirect("/billing/account/?message=Data Updated Successfully")
