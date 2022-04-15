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
from odoo import SUPERUSER_ID


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    # def action_validate_invoice_payment(self):
    def post(self):
        result = super(AccountPaymentInherit,self).post()
        if result:
            partner_id = self.invoice_ids[0].partner_id
            if partner_id.is_affiliate and partner_id.bought_membership:

                transaction_ids = list()

                for transaction in partner_id.transaction_ids:
                    if transaction.tran_invoice_id == self.invoice_ids[0]:
                        transaction_ids.append(transaction)

                for transaction_id in transaction_ids:
                    vals ={
                    'name': transaction_id.name,
                    'partner_id':transaction_id.partner_id.id,
                    'debit': transaction_id.credit,
                    'summary': transaction_id.summary,
                    'bonus_type': transaction_id.bonus_type,
                    #Kept for future use
                    # 'bonus_level_id': transaction_id.bonus_level_id.id,
                    'tran_invoice_id': transaction_id.tran_invoice_id.id,
                    'state':'paid',
                    }
                    self.env['mlm.transaction'].sudo().create(vals)
                    transaction_id.state = 'paid'

        return result
