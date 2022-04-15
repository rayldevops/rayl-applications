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
    _inherit = 'sale.order.line'

    @api.model
    def set_default_sale_order_line(self):
        so_id = [
        self.env.ref('affiliate_management_mlm.sale_order_6'),
        self.env.ref('affiliate_management_mlm.sale_order_7'),
        self.env.ref('affiliate_management_mlm.sale_order_8'),
        self.env.ref('affiliate_management_mlm.sale_order_9')
        ]

        mlm_config = self.env['affiliate.program'].get_mlm_configuration()

        for i in range(len(so_id)):

            vals = {
            "product_id": mlm_config.get('mlm_membership_product').product_variant_id.id,
            "order_id": so_id[i].id,
            }
            self.sudo().create(vals)
