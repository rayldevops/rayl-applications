from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import stripe
import time
import datetime
from odoo.http import request
import werkzeug


class BillingSetting(models.Model):
    _name = 'billing.setting'

    user_id = fields.Many2one('res.users', 'User Id', default=lambda self: self.env.user)
    # user_name = fields.Many2one('res.user','User Name')
    bank_id = fields.Many2one('bank.details', "Bank Name")
    payment_option = fields.Selection([('electronic_funds_transfer', 'electronic funds transfer'),
                                       ('credit_card', 'credit card')], string='Payment Option')
    branch_transit_number = fields.Char("Branch Transit Number")
    bank_account_number = fields.Char("Bank Account Number")
    mask_bank_account_number = fields.Char('Mask Bank Account Number')
    confirm_bank_account_number = fields.Char("Confirm Bank Account Number")

    stripe_card_id = fields.Char("Stripe Card Id")
    stripe_card_brand = fields.Char("Stripe Card Brand")
    stripe_card_customer = fields.Char("Stripe Card Customer")
    stripe_card_exp_month = fields.Char("Stripe Card Month")
    stripe_card_exp_year = fields.Char("Stripe Card Year")
    stripe_card_last4 = fields.Char("Stripe Card Last4")
    stripe_card_fingerprint = fields.Char("Stripe Card fingerprint")
    street_address = fields.Char("Street Address")
    post_code = fields.Char("Post Code")
    partner_id = fields.Many2one('res.partner', default=lambda self: self.env.user.partner_id.id)
    default_billing_id = fields.One2many('default.account', 'default_billing_id', string="Default")


class BillingAccount(models.Model):
    _name = 'billing.account'


#
#     billing_ids = fields.One2many('billing.setting', 'bank_id', string='Billing Id')
#     user_ids = fields.One2many('billing.setting', 'user_id', string='User Id')

# def mask_string(self, value):
#     print(value)
#     digits_to_keep = 4
#     return 1
#     mask_char = '#'
#     acc_number = value
#     num_of_digits = sum(map(str.isdigit, acc_number))
#     digits_to_mask = num_of_digits - digits_to_keep
#     masked_string = re.sub('\d', mask_char, acc_number, digits_to_mask)
#     return masked_string


class DefaultAccount(models.Model):
    _name = 'default.account'
    user_id = fields.Many2one('res.users', 'User Id', default=lambda self: self.env.user)
    default_billing_id = fields.Many2one('billing.setting', 'Default')


class ResPartner(models.Model):
    _inherit = 'res.partner'
    # province = fields.Char('Province')
    stripe_customer_id = fields.Text(string="Stripe Customer id")
    stripe_subscription_id = fields.Text(string="Stripe Subscription id")
    stripe_subscription_start_date = fields.Text(string="Subscription Last Invoice Date")
    stripe_subscription_end_date = fields.Text(string="Subscription Next Invoice Date")
    stripe_subscription_plan_description = fields.Text(string="Stripe Subscription Name")
    billing_setting_ids = fields.One2many("billing.setting", "partner_id")

    manual_start_date = fields.Date(string="Stripe Subscription Start Date")
    manual_affiliate_program = fields.Many2one('product.product', string="Affiliate Program")

    def create_manual_sub(self):
        start_date = self.manual_start_date
        plan_id = self.manual_affiliate_program['stripe_plan_id']
        customer_id = self.stripe_customer_id
        stripe_data = self.env['payment.acquirer'].sudo().search([('state', '=', 'enabled'),
                                                                  ('provider', '=', 'stripe')])
        date_string = start_date.strftime('%Y-%m-%d')
        end_date = start_date + datetime.timedelta(days=30)
        start_date_time_stamp = round(time.mktime(datetime.datetime.strptime(date_string, "%Y-%m-%d").timetuple()))
        if customer_id:
            if plan_id:
                try:
                    stripe.api_key = stripe_data.stripe_secret_key
                    res_sub = stripe.Subscription.create(
                        customer=customer_id,
                        items=[
                            {"price": plan_id},
                        ],
                        trial_end=start_date_time_stamp,
                    )
                    if res_sub:
                        res_prod = self.env['product.product'].sudo().search([('stripe_plan_id', '=', plan_id)])
                        res_part = self.env['res.partner'].sudo().search([('stripe_customer_id', '=', customer_id)])
                        res_part.sudo().write({
                            'stripe_subscription_start_date': start_date,
                            'stripe_subscription_end_date': end_date,
                            'stripe_subscription_plan_description': res_prod.name,
                            'stripe_subscription_id': res_sub.id,
                        })
                        # sale_order_id = self.env['sale.order'].sudo().search([('state', '=', 'sale')], order='id desc',
                        #                                                     limit=1)
                        pay_trans = self.env['payment.transaction'].sudo().search(
                            [('state', '=', 'done'), ('partner_id', '=', res_part.id)],
                            order='id desc',
                            limit=1)
                        pay_trans.sudo().write({
                            'stripe_subscription_id': res_sub.id,
                            'amount': res_prod.list_price
                        })

                        # inv_obj = self.env['account.move'].sudo().create({
                        #     'move_type': 'out_invoice',
                        #     'partner_id': res_part.id,
                        #     'currency_id': res_prod.currency_id.id,
                        #     'invoice_line_ids': [(0, 0, {
                        #         'price_unit': res_prod.list_price,
                        #         'quantity': 1.0,
                        #         'product_id': res_prod.id,
                        #     })],
                        # })


                except stripe.error.CardError as e:
                    # Since it's a decline, stripe.error.CardError will be caught
                    raise ValidationError(e)
                except stripe.error.RateLimitError as e:
                    # Too many requests made to the API too quickly
                    raise ValidationError(e)
                except stripe.error.InvalidRequestError as e:
                    # Invalid parameters were supplied to Stripe's API
                    raise ValidationError(e)
                except stripe.error.AuthenticationError as e:
                    # Authentication with Stripe's API failed
                    # (maybe you changed API keys recently)
                    raise ValidationError(e)
                except stripe.error.APIConnectionError as e:
                    # Network communication with Stripe failed
                    raise ValidationError(e.user_message)
                except stripe.error.StripeError as e:
                    # Display a very generic error to the user, and maybe send
                    # yourself an email
                    raise ValidationError(e)
                except Exception as e:
                    # Something else happened, completely unrelated to Stripe
                    raise ValidationError(e)
            else:
                raise ValidationError("Product Not found")
        else:
            raise ValidationError("Customer Id Does Not Exist Please Ask Customers to Add Billing Details")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    stripe_plan_id = fields.Text(string="Stripe Plan id")
    stripe_product_id = fields.Text(string="Stripe Product id")


class Users(models.Model):
    _inherit = 'res.users'

    billing_ids = fields.One2many('billing.setting', 'user_id')


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_gateway_reference = fields.Text(string="Payment Gateway Reference")

