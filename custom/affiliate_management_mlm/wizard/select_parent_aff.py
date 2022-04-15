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

from odoo import api, models, fields, _
from odoo import exceptions


class SelectParentAffiliate(models.TransientModel):
    _name = 'select.parent.aff'
    _description = "Select Parent Aff"

    parent_aff = fields.Many2one(string="Parent Affiliate", comodel_name="res.partner", domain="[('is_affiliate','=',True),('bought_membership','=',True),'|',('left_child_aff','=',False),('right_child_aff','=',False)]", context="{'name_get_override':True}")

    def set_parent_aff(self):
        if self.env.context.get('active_model') == 'affiliate.request' and self.env.context.get('active_id'):
            active_model = self.env.context.get('active_model')
            active_id = self.env.context.get('active_id')

            aff_request_id = self.env[active_model].browse(active_id)

            if not aff_request_id.parent_aff_key:

                aff_request_id.parent_aff_key = self.parent_aff.res_affiliate_key

                aff_request_id.partner_id.parent_aff = self.parent_aff.id

                aff_request_id.partner_id.is_dispute = False
                aff_request_id.partner_id.dispute_remark = ""

            else:
                raise exceptions.ValidationError(
                _("""Error while validating constraint
                Error ! Parent Affiliate is already assigned.
                """))
