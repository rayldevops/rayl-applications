from odoo import http, _
from odoo.http import request
import werkzeug
import logging
_logger = logging.getLogger(__name__)
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteAffiliateMLM(WebsiteSale):

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation(self, **post):
        result = super(WebsiteAffiliateMLM,self).payment_confirmation(**post)

        order = result.qcontext.get('order')
        mlm_config = request.env['affiliate.program'].sudo().get_mlm_configuration()
        if mlm_config.get('mlm_membership_product').product_variant_id.id in [ol.product_id.id for ol in order.order_line]:
            if order.partner_id.membership_state == 'initial':
                order.partner_id.membership_state = 'draft'
        return result
