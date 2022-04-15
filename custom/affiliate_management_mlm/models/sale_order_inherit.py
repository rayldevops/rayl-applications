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
import logging
_logger = logging.getLogger(__name__)

from odoo import api, fields, models, _


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def check_partner_product(self):
        aff_ids = self.env['affiliate.request'].sudo().search([])
        partner_id = self.partner_id
        mlm_product = self.env['website'].get_mlm_product().product_variant_id

        if partner_id in [id.partner_id for id in aff_ids]:
            if len(self.env["sale.order.line"].sudo().search(["&",("order_id","=",self.id),("product_id","=",mlm_product.id)])) == 1:
                return True
        return False

    def check_partner_upgrade_product(self):
        aff_ids = self.env['affiliate.request'].sudo().search([])
        partner_id = self.partner_id
        mlm_upgrade_product = self.env['website'].get_mlm_upgrade_product().product_variant_id

        if mlm_upgrade_product:
            if partner_id in [id.partner_id for id in aff_ids]:
                if len(self.env["sale.order.line"].sudo().search(["&",("order_id","=",self.id),("product_id","=",mlm_upgrade_product.id)])) == 1:
                    return True
        return False

    def check_partner_bundle_product(self):
        aff_ids = self.env['affiliate.request'].sudo().search([])
        partner_id = self.partner_id
        mlm_bundle_product = self.env['website'].get_mlm_bundle_product().product_variant_id

        if mlm_bundle_product:
            if partner_id in [id.partner_id for id in aff_ids]:
                if len(self.env["sale.order.line"].sudo().search(["&",("order_id","=",self.id),("product_id","=",mlm_bundle_product.id)])) == 1:
                    return True
        return False

    def action_confirm(self):
        result = super(SaleOrderInherit,self).action_confirm()
        if self.check_partner_product():
            self.partner_id.mlm_order_id = self.id
            self.partner_id.bought_membership = True
            aff_obj = self.env['affiliate.request'].sudo().search([('partner_id', '=',  self.partner_id.id)])
            self.partner_id.membership_state = 'approve'
            if aff_obj:
                aff_obj.write({'parent_aff_key': aff_obj.website_parent_affiliate_key,
                               'show_menus': True})
                parent_partner = self.env['res.partner'].sudo().search(
                    [('res_affiliate_key', '=', aff_obj.website_parent_affiliate_key)], limit=1)
                affiliate_partner = self.env['res.partner'].sudo().search(
                    [('id', '=', self.partner_id.id)], limit=1)
                affiliate_partner.write({'parent_aff': parent_partner.id if parent_partner else False})
                parent_partner.write({'child_aff': [(4, self.partner_id.id)]})
                line_id = 0
                line_product_id = 0
                for line in self.order_line:
                    line_id = line.id
                    line_product_id = line.product_id.id
                visit_obj = self.env['affiliate.visit'].sudo()
                visit = visit_obj.create({
                    'affiliate_method': 'pps',
                    'affiliate_key': self.partner_id.res_affiliate_key,
                    'parent_affiliate_partner_id': self.partner_id.parent_aff.id,
                    'affiliate_partner_id': self.partner_id.id,
                    'url': "",
                    'affiliate_type': 'product',
                    'type_name': line_product_id,
                    'sales_order_line_id': line_id,
                    'convert_date': fields.datetime.now(),
                    'affiliate_program_id': self.partner_id.affiliate_program_id.id,
                    'product_quantity': '1',
                    'commission_amt': self.partner_id.affiliate_program_id.amount,
                    'tier1': True,
                    'is_converted': True
                })
                # parent_aff_partner = self.env['res.partner'].sudo().search(
                #     [('id', '=', self.partner_id.parent_aff.parent_aff.id)], limit=1)
                # if parent_aff_partner:
                #     parent_visit = visit_obj.create({
                #         'affiliate_method': 'pps',
                #         'affiliate_key': self.partner_id.res_affiliate_key,
                #         'parent_affiliate_partner_id': parent_aff_partner.id,
                #         'affiliate_partner_id': self.partner_id.id,
                #         'url': "",
                #         'affiliate_type': 'product',
                #         'type_name': line_product_id,
                #         'sales_order_line_id': line_id,
                #         'convert_date': fields.datetime.now(),
                #         'affiliate_program_id': self.partner_id.affiliate_program_id.id,
                #         'product_quantity': '1',
                #         'commission_amt': self.partner_id.affiliate_program_id.tier2_amount,
                #         'tier2': True,
                #         'is_converted': True
                #     })
            if not self.partner_id.parent_aff and not self.partner_id.aff_request_id.parent_aff_key:
                self.partner_id.is_dispute = True
                self.partner_id.dispute_remark = _("Parent Affiliate is missing.")
        if self.partner_id.bought_membership:
            if self.check_partner_upgrade_product():
                # aff_obj = self.env['affiliate.request'].sudo().search([('partner_id', '=', self.partner_id.id)], limit=1)
                aff_obj = self.env['affiliate.request'].sudo().search([('partner_id', '=', self.partner_id.id),
                                                                       ('upgrade_membership', '=', False)], limit=1)
                if aff_obj:
                    parent_partner = self.env['res.partner'].sudo().search(
                        [('res_affiliate_key', '=', aff_obj.website_parent_affiliate_key)], limit=1)
                    affiliate_partner = self.env['res.partner'].sudo().search(
                        [('id', '=', self.partner_id.id)], limit=1)
                    affiliate_partner.write({'parent_aff': parent_partner.id if parent_partner else False})
                    parent_partner.write({'child_aff': [(4, self.partner_id.id)]})
                    line_id = 0
                    line_product_id = 0
                    for line in self.order_line:
                        line_id = line.id
                        line_product_id = line.product_id.id
                    visit_obj = self.env['affiliate.visit'].sudo()
                    visit = visit_obj.create({
                        'affiliate_method': 'pps',
                        'affiliate_key': self.partner_id.res_affiliate_key,
                        'parent_affiliate_partner_id': self.partner_id.parent_aff.id,
                        'affiliate_partner_id': self.partner_id.id,
                        'url': "",
                        'affiliate_type': 'product',
                        'type_name': line_product_id,
                        'sales_order_line_id': line_id,
                        'convert_date': fields.datetime.now(),
                        'affiliate_program_id': self.partner_id.affiliate_program_id.id,
                        'product_quantity': '1',
                        'commission_amt': self.partner_id.affiliate_program_id.up_tier1_amount,
                        'tier1': True,
                        'is_converted': True
                    })
                    self.partner_id.mlm_order_id = self.id
                    self.partner_id.upgrade_membership = True
                    self.partner_id.bought_membership = True
                    # parent_aff_partner = self.env['res.partner'].sudo().search(
                    #     [('id', '=', self.partner_id.parent_aff.parent_aff.id)], limit=1)
                    # if parent_aff_partner:
                    #     parent_visit = visit_obj.create({
                    #         'affiliate_method': 'pps',
                    #         'affiliate_key': self.partner_id.res_affiliate_key,
                    #         'parent_affiliate_partner_id': parent_aff_partner.id,
                    #         'affiliate_partner_id': self.partner_id.id,
                    #         'url': "",
                    #         'affiliate_type': 'product',
                    #         'type_name': line_product_id,
                    #         'sales_order_line_id': line_id,
                    #         'convert_date': fields.datetime.now(),
                    #         'affiliate_program_id': self.partner_id.affiliate_program_id.id,
                    #         'product_quantity': '1',
                    #         'commission_amt': self.partner_id.affiliate_program_id.up_tier2_amount,
                    #         'tier2': True,
                    #         'is_converted': True
                    #     })
        if self.check_partner_bundle_product():
            aff_obj = self.env['affiliate.request'].sudo().search([('partner_id', '=', self.partner_id.id),
                                                                   ('bought_membership', '=', False)], limit=1)
            if aff_obj:
                parent_partner = self.env['res.partner'].sudo().search(
                    [('res_affiliate_key', '=', aff_obj.website_parent_affiliate_key)], limit=1)
                affiliate_partner = self.env['res.partner'].sudo().search(
                    [('id', '=', self.partner_id.id)], limit=1)
                affiliate_partner.write({'parent_aff': parent_partner.id if parent_partner else False})
                parent_partner.write({'child_aff': [(4, self.partner_id.id)]})
                line_id = 0
                line_product_id = 0
                for line in self.order_line:
                    line_id = line.id
                    line_product_id = line.product_id.id
                visit_obj = self.env['affiliate.visit'].sudo()
                visit = visit_obj.create({
                    'affiliate_method': 'pps',
                    'affiliate_key': self.partner_id.res_affiliate_key,
                    'parent_affiliate_partner_id': self.partner_id.parent_aff.id,
                    'affiliate_partner_id': self.partner_id.id,
                    'url': "",
                    'affiliate_type': 'product',
                    'type_name': line_product_id,
                    'sales_order_line_id': line_id,
                    'convert_date': fields.datetime.now(),
                    'affiliate_program_id': self.partner_id.affiliate_program_id.id,
                    'product_quantity': '1',
                    'commission_amt': self.partner_id.affiliate_program_id.bundle_tier1_amount,
                    'tier1': True,
                    'is_converted': True
                })
                self.partner_id.mlm_order_id = self.id
                self.partner_id.upgrade_membership = True
                self.partner_id.bought_membership = True
                # parent_aff_partner = self.env['res.partner'].sudo().search(
                #     [('id', '=', self.partner_id.parent_aff.parent_aff.id)], limit=1)
                # if parent_aff_partner:
                #     parent_visit = visit_obj.create({
                #         'affiliate_method': 'pps',
                #         'affiliate_key': self.partner_id.res_affiliate_key,
                #         'parent_affiliate_partner_id': parent_aff_partner.id,
                #         'affiliate_partner_id': self.partner_id.id,
                #         'url': "",
                #         'affiliate_type': 'product',
                #         'type_name': line_product_id,
                #         'sales_order_line_id': line_id,
                #         'convert_date': fields.datetime.now(),
                #         'affiliate_program_id': self.partner_id.affiliate_program_id.id,
                #         'product_quantity': '1',
                #         'commission_amt': self.partner_id.affiliate_program_id.tier2_amount  + self.partner_id.affiliate_program_id.up_tier2_amount,
                #         'tier2': True,
                #         'is_converted': True
                #     })
        #visit.action_confirm()
        return result

    def action_cancel(self):
        result = super(SaleOrderInherit,self).action_cancel()
        if self.check_partner_product():
            self.partner_id.membership_state = 'cancel'
        return result
