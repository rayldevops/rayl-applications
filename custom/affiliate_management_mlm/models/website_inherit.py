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

from odoo import api, fields, models


class WebsiteInherit(models.Model):
    _inherit = 'website'

    def get_mlm_product(self):
        id = self.env['affiliate.program'].sudo().search([],limit=1)
        product = id.mlm_membership_product
        return product

    def get_mlm_upgrade_product(self):
        id = self.env['affiliate.program'].sudo().search([],limit=1)
        if id.upgrade_membership_product:
            product = id.upgrade_membership_product
            return product
        return False

    def get_mlm_bundle_product(self):
        id = self.env['affiliate.program'].sudo().search([],limit=1)
        product = id.bundle_membership_product
        return product

    def check_membership(self):
        # aff_request = self.env["affiliate.request"].sudo().search([("partner_id","=",self.env.user.partner_id.id)])
        # bought_membership = False
        # if aff_request:
        # bought_membership = True if aff_request.partner_id.bought_membership else False

        if self.env.user.partner_id.bought_membership:
            return True

        return False


    def get_affiliate_request(self):
        aff_request = self.env["affiliate.request"].sudo().search([("partner_id","=",self.env.user.partner_id.id)])
        return aff_request

#--------------------------MLM Tree-------Start------->

    def tree_width(self, root):
        node_width = 11

        width = root.mlm_tree(root).get('width')

        return width * node_width

    def get_mlm_tree_details(self, root):
        return root.mlm_tree(root)

#--------------------------MLM Tree-------End------->
