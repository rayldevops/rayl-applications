from odoo import http,_
from odoo.http import request
import requests
import json
import logging
_logger = logging.getLogger(__name__)


class PaypalSubscription(http.Controller):

    @http.route(['/confirm_subscription'], auth='public', type='http', website=True, methods=['POST'], csrf=False)
    def confirm_subscription(self, **post):
        orders = []
        paypal_token_url = 'https://api-m.sandbox.paypal.com/v1/oauth2/token'
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
        }
        data = {
            'grant_type': 'client_credentials'
        }
        client_id = 'ARudoJr-eUBYZjuWZ09NylFUb9VX2mkASKlvBnpsfUg_y4gVMrczM6QH9y4Nqn8HHJGgGR_YydkAiUCC'
        client_secret = 'ECQ5hefjIgd6FwhoC3kJ3CAEG5O5hGhe8FIdwIvgPKWMO4gaC-NJzlgeQhQj6yGxvTQZjHZ6uucWNddN'
        paypal_token = requests.post(paypal_token_url, headers=headers, data=data, auth=(client_id, client_secret))

        content = json.loads(paypal_token.content.decode('utf-8'))
        auth_header = "Bearer {0}".format(content['access_token'])

        headers = {
            'Content-Type': 'application/json',
            'Authorization': auth_header,
        }

        order_url = 'https://api-m.sandbox.paypal.com/v2/checkout/orders/' + post.get('datas[orderID]')

        order_response = requests.get(order_url, headers=headers)

        res = json.loads(order_response.content.decode("utf-8"))

        subscription_obj = request.env['sale.subscription'].sudo()

        partner_serach = request.env['res.partner'].sudo().search([('name', '=', res['payer']['name']['given_name'] + " " + res['payer']['name']['surname'])], limit=1)

        if partner_serach:
            partner = partner_serach
        else:
            partner = request.env['res.partner'].sudo().create({
                'name': res['payer']['name']['given_name'] + " " + res['payer']['name']['surname'],
                'email': res['payer']['email_address']
            })
        product_search = request.env['product.product'].sudo().search([('paypal_plan_id', '=', post.get('plan_id'))], limit=1)

        subscription = subscription_obj.create({
            'partner_id': partner.id,
            'template_id': 1,
            'code': post.get('datas[subscriptionID]'),
            'recurring_invoice_line_ids': [(0,0, {
                        'product_id': product_search.id,
                        'quantity': 1,
                        'uom_id': product_search.uom_id.id,
                        'price_unit': product_search.lst_price
                    })]
        })

        request.env.cr.commit()