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
from odoo import SUPERUSER_ID
from odoo import exceptions

class AffilaiteRequestInherit(models.Model):
    _inherit = 'affiliate.request'

    bought_membership = fields.Boolean(string="Bought Membership",related="partner_id.bought_membership")
    upgrade_membership = fields.Boolean(string="Upgrade Membership",related="partner_id.upgrade_membership" )
    is_dispute = fields.Boolean(string="Is In Dispute", related="partner_id.is_dispute")
    dispute_remark = fields.Text(string="Remark", readonly=True, related="partner_id.dispute_remark")

    def get_request_record(self,name):
        return self.search([('name','=',name)],limit = 1)

    def _compute_signup_valid(self):
        try:
            self.ensure_one()
        except(ValueError):
            super(AffilaiteRequestInherit,self[0])._compute_signup_valid()
        else:
            super(AffilaiteRequestInherit,self)._compute_signup_valid()

    def action_cancel(self):
        mlm_config = self.env['affiliate.program'].get_mlm_configuration()
        # return self.env['custom.dialog.box'].dialog_box(msg="msg", title="Approved")

        if self.partner_id.is_affiliate and self.bought_membership:
            if self.partner_id == mlm_config.get('root'):
                raise exceptions.ValidationError("Please, change the RAP root before removing this partner as Affiliate.")

            self.partner_id.parent_aff = False
            if self.partner_id.left_child_aff:
                self.partner_id.left_child_aff.parent_aff = False
                self.partner_id.left_child_aff = False

            if self.partner_id.right_child_aff:
                self.partner_id.right_child_aff.parent_aff = False
                self.partner_id.right_child_aff = False

            self.partner_id.is_dispute = True
            self.parent_aff_key = ""
            self.partner_id.dispute_remark = _("Parent Affiliate Key is Empty. Before approve, please set a parent affiliate for this partner.")

        return super(AffilaiteRequestInherit,self).action_cancel()


    def validate_request(self, parent_key):
        key_parent_id = self.env['res.partner'].affi_key_check(parent_key)
        # parent_id = self.partner_id.parent_aff

        # if not key_parent_id and not parent_id and self.bought_membership:
        if not key_parent_id and self.bought_membership:
            self.partner_id.is_dispute = True
            if not parent_key:
                self.partner_id.dispute_remark = _("Parent Affiliate Key is Empty. Before approve, please set a parent affiliate for this partner.")
            else:
                self.parent_aff_key = ""
                self.partner_id.dispute_remark = _("Parent Affiliate Key is Invalid. Before approve, please set a parent affiliate for this partner.")
            self.env.cr.commit()

            raise exceptions.ValidationError(self.dispute_remark)

        elif key_parent_id and not key_parent_id.bought_membership and self.bought_membership:
            self.partner_id.is_dispute = True
            self.parent_aff_key = ""
            self.partner_id.dispute_remark = _("Parent Affiliate Key is Invalid. As provided parent affiliate is not having the Membership. Please change the parent affiliate for this partner.")
            self.env.cr.commit()
            raise exceptions.ValidationError(self.dispute_remark)

        # elif key_parent_id and not self.partner_id.check_parent_childs(key_parent_id) or parent_id and not self.partner_id.check_parent_childs(parent_id):
        elif key_parent_id and key_parent_id.bought_membership and self.bought_membership and not self.partner_id.check_parent_childs(key_parent_id):
            self.partner_id.is_dispute = True
            self.parent_aff_key = ""
            self.partner_id.dispute_remark = _("Both the childs of parent affiliate are occupied. Please change the parent affiliate for this partner.")
            self.env.cr.commit()
            raise exceptions.ValidationError(self.dispute_remark)

        elif (key_parent_id and key_parent_id.bought_membership and not self.bought_membership) or (parent_key and not self.bought_membership):
            raise exceptions.ValidationError(_("Multi Level Marketing Membership is Missing for this partner."))

        # elif key_parent_id and not key_parent_id.bought_membership or parent_id and not parent_id.bought_membership:
        #     raise exceptions.ValidationError(_("Parent Affiliate Membership Plan is Missing."))

        # elif not key_parent_id and self.partner_id.parent_aff:
        #     result = super(AffilaiteRequestInherit,self).action_aproove()
        #     self.partner_id.parent_aff = self.partner_id.parent_aff.id
        #
        #     position = "<strong><em>Left Child Affiliate</em></strong>" if self.partner_id.parent_aff.left_child_aff == self.partner_id else "<strong><em>Right Child Affiliate</em></strong>"
        #     msg = "<strong>"+ self.partner_id.name+ "</strong>" + " is now the " + position + " of " + "<strong>" +self.partner_id.parent_aff.name +"</strong>."
        #     response = self.env['custom.dialog.box'].dialog_box(msg=msg, title="Approved")
        #
        #     return response

        return key_parent_id

    def action_aproove(self):

        key_parent_id = self.validate_request(self.parent_aff_key)
        if key_parent_id and key_parent_id.bought_membership and self.bought_membership:
            result = super(AffilaiteRequestInherit,self).action_aproove()
            self.partner_id.parent_aff = key_parent_id.id
            self.partner_id.provide_level_commission = True
            position = "<strong><em>Left Child Affiliate</em></strong>" if self.partner_id.parent_aff.left_child_aff == self.partner_id else "<strong><em>Right Child Affiliate</em></strong>"
            msg = "<strong>"+ self.partner_id.name+ "</strong>" + " is now the " + position + " of " + "<strong>" +self.partner_id.parent_aff.name +"</strong>."

            response = self.env['custom.dialog.box'].dialog_box(msg=msg, title="Approved")
            return response

        return super(AffilaiteRequestInherit,self).action_aproove()


    #Kept for future use
    #Automatic Insertion Algo code is this

    # def _insert(self,roots):
    #
    #     childs = list()
    #     for root in roots:
    #         if not root.left_child_aff:
    #             root.left_child_aff = self.partner_id
    #             # self.partner_id.parent_aff = root
    #             return True
    #
    #         if not root.right_child_aff:
    #             root.right_child_aff = self.partner_id
    #             # self.partner_id.parent_aff = root
    #             return True
    #
    #         childs.append(root.left_child_aff)
    #         childs.append(root.right_child_aff)
    #
    #     self._insert(childs)
    #
    # def get_root(self,mlm_config):
    #     if mlm_config["insertion_type"] == 'loi':
    #         root = mlm_config['root']
    #     else:
    #         root = self.env['res.partner'].search([("res_affiliate_key","=",self.parent_aff_key)])
    #     return root

    # def action_aproove(self):
    #     result = super(AffilaiteRequestInherit,self).action_aproove()
    #
    #     mlm_config = self.env['affiliate.program'].get_mlm_configuration()
    #
    #     if mlm_config["insertion_type"] and mlm_config["mlm_membership_product"]:
    #         root = self.get_root(mlm_config)
    #         self._insert(root)
    #
    #     return result
