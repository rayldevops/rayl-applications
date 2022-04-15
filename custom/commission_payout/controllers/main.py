from odoo import fields, http
from odoo.http import request
import odoo
from odoo.exceptions import AccessError, UserError, AccessDenied
from lxml import etree

#
# class BillingAccounts():
#     @http.route(['/my/billing'], type='http', auth="public", website=True, sitemap=False)
#     def my_billing(self, **post):
#         print('a',a)
        # config = request.env['ir.config_parameter'].sudo().search([('key','=','website_terms_conditions.terms_and_conditions')])
        # a = config.value

        # return request.render("website_terms_conditions.terms_condition", {'setting': a})
