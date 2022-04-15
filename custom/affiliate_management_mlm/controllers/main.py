# -*- coding: utf-8 -*-
#################################################################################
# Author : Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
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
from odoo.addons.affiliate_management.controllers.affiliate_website import website_affiliate


class WebsiteAffiliateMLM(website_affiliate):

    @http.route('/affiliate/register', auth='public',type='http', website=True)
    def register_affiliate(self, **kw):
        result = super(WebsiteAffiliateMLM,self).register_affiliate(**kw)
        if result.headers.get('Location') == '/affiliate' and not request.session.get('error',None):
            aff_request = request.env['affiliate.request'].sudo().search([("name","=",kw.get("login") or kw.get("email"))])
            aff_request.parent_aff_key = kw.get("aff_key")
            aff_request.partner_id.aff_request_id = aff_request.id

        return result

    @http.route("/affiliate/request", type='json', auth="public", methods=['POST'], website=True)
    def portal_user(self, user_id,**kw):
        result = super(WebsiteAffiliateMLM,self).portal_user(user_id,**kw)

        if result:
            aff_request = request.env["affiliate.request"].sudo().search([("partner_id","=",request.env.user.partner_id.id)])
            aff_request.partner_id.aff_request_id = aff_request.id

        return result

    @http.route('/affiliate/membership/', auth='public',type='http', website=True)
    def mlm_membership(self, **kw):

        # credit_card_info = request.env['billing.setting'].sudo().search([('user_id','=',request.env.user.id)])
        # if len(credit_card_info) <= 0:
        #     return request.redirect('/my/billing/?error=Please Update Billing Settings to purchase Subscription')

        product = request.website.get_mlm_product()
        bundle_product = request.website.get_mlm_bundle_product()
        mlm_config = request.env['affiliate.program'].sudo().get_mlm_configuration()

        values={
        "product_temp_id": product,
        "bundle_product_temp_id":bundle_product,
        "mlm_work_title": mlm_config.get('mlm_work_title'),
        "mlm_work_text": mlm_config.get('mlm_work_text'),
        }

        return http.request.render('affiliate_management_mlm.mlm_membership',values)

    @http.route('/affiliate/upgrade_membership', auth='public', type='http', website=True)
    def mlm_upgrade_membership(self, **kw):
        product = request.website.get_mlm_upgrade_product()
        mlm_config = request.env['affiliate.program'].sudo().get_mlm_configuration()

        values = {
            "product_temp_id": product,
            "mlm_work_title": mlm_config.get('mlm_work_title'),
            "mlm_work_text": mlm_config.get('mlm_work_text'),
        }

        return http.request.render('affiliate_management_mlm.mlm_upgrade_membership', values)

    @http.route('/affiliate/buy-membership', auth='public',type='http', website=True)
    def buy_membership(self, **kw):
        if request.env.uid == request.env.ref('base.public_user').id:
            return request.redirect("/web/login")
        return request.redirect("/affiliate/mlm-product-add")


    @http.route('/affiliate/mlm-product-add', auth='user',type='http', website=True)
    def mlm_membership_sol(self, **kw):

        sale_order_id = request.website.sale_get_order()
        product_id = request.website.get_mlm_product()

        if not sale_order_id:
            sale_order_id = request.website.sale_get_order(force_create = True)

        order = request.website.sale_get_order()
        if order:
            for line in order.website_order_line:
                line.unlink()
        if len(request.env["sale.order.line"].sudo().search(["&",("order_id","=",sale_order_id.id),("product_id","=",product_id.product_variant_id.id)])) == 0:
            vals={
                    "product_id":product_id.product_variant_id.id,
                    "order_id":sale_order_id.id
                }
            request.env["sale.order.line"].sudo().browse().unlink()
            request.env['sale.order.line'].sudo().create(vals)

        return request.redirect("/shop/cart")

    @http.route('/affiliate/mlm-product-upgrade', auth='user', type='http', website=True)
    def mlm_upgrade_membership_sol(self, **kw):

        sale_order_id = request.website.sale_get_order()
        product_id = request.website.get_mlm_upgrade_product()

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
            request.env['sale.order.line'].sudo().create(vals)

        return request.redirect("/shop/cart")

    @http.route('/affiliate/mlm-product-bundle', auth='user', type='http', website=True)
    def mlm_bundle_membership_sol(self, **kw):

        sale_order_id = request.website.sale_get_order()
        product_id = request.website.get_mlm_bundle_product()

        if not sale_order_id:
            sale_order_id = request.website.sale_get_order(force_create=True)

        order = request.website.sale_get_order()
        if order:
            for line in order.website_order_line:
                line.unlink()
        if len(request.env["sale.order.line"].sudo().search(["&", ("order_id", "=", sale_order_id.id), (
        "product_id", "=", product_id.product_variant_id.id)])) == 0:
            vals = {
                "product_id": product_id.product_variant_id.id,
                "order_id": sale_order_id.id
            }

            request.env['sale.order.line'].sudo().create(vals)

        return request.redirect("/shop/cart")

    @http.route('/shop/cart/mlm_product/remove/<line_id>', auth='public',type='http', website=True)
    def remove_affiliate_discount(self, line_id = 0):
        if line_id:
            request.env["sale.order.line"].sudo().browse([int(line_id)]).unlink()
        return request.redirect("/shop/cart/")

    @http.route('/affiliate/mlm_tree',auth = 'user', type = 'http', website = True)
    def mlm_tree(self):
        user_partner_id = request.env.user.partner_id

        values={
            "user_partner_id": user_partner_id,
        }

        return http.request.render('affiliate_management_mlm.mlm_tree', values)

    # @http.route('/affiliate/', auth='public',type='http', website=True)
    # def affiliate(self, **kw):
    #     result = super(WebsiteAffiliateMLM,self).affiliate(**kw)
    #     mlm_config = request.env['affiliate.program'].sudo().get_mlm_configuration()
    #     vals={
    #         "mlm_work_title": mlm_config.get('mlm_work_title'),
    #         "mlm_work_text": mlm_config.get('mlm_work_text'),
    #     }
    #     result.qcontext.update(vals)
    #
    #     return result

    @http.route('/affiliate/about',type='http', auth="user", website=True)
    def affiliate_about(self, **kw):
        result = super(WebsiteAffiliateMLM,self).affiliate_about(**kw)
        vals={
            "affiliate_about": True,
        }
        result.qcontext.update(vals)

        return result

    @http.route(['/affiliate/mlm_bonus','/affiliate/mlm_bonus/<int:page>'],type='http', auth="user", website=True)
    def affiliate_mlm_bonus(self, page=1, **kw):
        user_partner_id = request.env.user.partner_id
        debit_transactions = list()
        currency_id = request.env.user.company_id.currency_id
        total_bonus = 0
        for tran in user_partner_id.transaction_ids:
            if tran.state == 'paid' and tran.debit:
                debit_transactions.append(tran)
                total_bonus += tran.debit

        trans_count = len(debit_transactions)
        pager = request.website.pager(
            url='/affiliate/mlm_bonus',
            total=trans_count,
            page=page,
            step=10
        )

        debit_transactions = debit_transactions[pager['offset']:]

        values={
            "pager": pager,
            "debit_transactions": debit_transactions,
            "user_partner_id": user_partner_id,
            "total_bonus":total_bonus,
            "currency_id":currency_id,
        }

        return http.request.render('affiliate_management_mlm.mlm_bonus', values)

    @http.route(['/my/bonus/<int:transaction>'], type='http', auth="user", website=True)
    def aff_bonus_form(self, transaction=None, **kw):
        tran = request.env['mlm.transaction'].sudo().browse([transaction])
        return request.render("affiliate_management_mlm.bonus_transaction_form", {
            'tran': tran,
        })

    @http.route(['/my/invoice/<int:invoice>'], type='http', auth="user", website=True)
    def aff_invoice_form(self, invoice=None, **kw):
        result = super(WebsiteAffiliateMLM, self).aff_invoice_form(invoice= invoice, **kw)
        invoice = result.qcontext.get('invoice')

        if invoice.is_invoice_of == 'bonus':
            return http.request.render('affiliate_management_mlm.mlm_payment_form',result.qcontext)
        return result

    @http.route('/affiliate/signup', auth='public',type='http', website=True)
    def register(self, **kw):
        result = super(WebsiteAffiliateMLM, self).register(**kw)
        mlm_config = request.env['affiliate.program'].sudo().get_mlm_configuration()
        values = {
        'about_ref_code':mlm_config.get("about_ref_code")
        }
        result.qcontext.update(values)
        return result

    @http.route(['/affiliate/affiliate-referal-key'], type='json', auth="public", website=True)
    def aff_referal_key(self, **kw):
        user_partner_id = request.env.user.partner_id
        key_parent_id = request.env['res.partner'].affi_key_check(kw.get('affi_ref_key'))
        aff_request_id = request.env['affiliate.request'].sudo().search([('partner_id','=',user_partner_id.id)],limit=1)

        # if key_parent_id and key_parent_id.bought_membership and not aff_request_id.parent_aff_key:
        if key_parent_id and key_parent_id != user_partner_id and key_parent_id.bought_membership:
            if user_partner_id.bought_membership and not user_partner_id.check_parent_childs(key_parent_id):
                user_partner_id.is_dispute = True
                user_partner_id.dispute_remark = _("Provided parent affiliate's both child are occupied.")
                return 1

            if user_partner_id.bought_membership:
                user_partner_id.parent_aff = key_parent_id.id

            if user_partner_id.bought_membership and user_partner_id.is_dispute:
                user_partner_id.is_dispute = False
            return 2

        return 3

    @http.route(['/affiliate/signup-referal-key'], type='json', auth="public", website=True)
    def signup_referal_key(self, **kw):
        user_partner_id = request.env.user.partner_id
        key_parent_id = request.env['res.partner'].affi_key_check(kw.get('affi_ref_key'))
        # aff_request_id = request.env['affiliate.request'].sudo().search([('partner_id','=',user_partner_id.id)],limit=1)

        if key_parent_id and key_parent_id.bought_membership:
            return {"response":True}
        elif not key_parent_id:
            return {"response":False, "msg":"Affiliate Referral key is Invalid."}

        return {"response":False, "msg":"Found the affilaite referral key but is not a Multi Level Marketing member."}

    @http.route(['/affiliate/check-affiliate'], type='json', auth="public", website=True)
    def aff_check(self, **kw):
        if not request.env.user.partner_id.is_affiliate and not request.env.user.partner_id.aff_request_id.parent_aff_key:
            return False
        return "/affiliate/mlm-product-add"

    @http.route(['/affiliate/check-upgrade'], type='json', auth="public", website=True)
    def aff_check_upgrade(self, **kw):
        if not request.env.user.partner_id.is_affiliate and not request.env.user.partner_id.aff_request_id.parent_aff_key:
            return False
        return "/affiliate/mlm-product-upgrade"

    @http.route(['/affiliate/check-bundle'], type='json', auth="public", website=True)
    def aff_check_bundle(self, **kw):
        if not request.env.user.partner_id.is_affiliate and not request.env.user.partner_id.aff_request_id.parent_aff_key:
            return False
        return "/affiliate/mlm-product-bundle"
