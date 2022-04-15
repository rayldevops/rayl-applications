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
from odoo.exceptions import UserError
from odoo import models, fields,api,_
import random, string
class AccountInvoiceInherit(models.Model):
    _inherit = 'account.move'

    mlm_transaction_id = fields.One2many(string="RAP Transaction ID", comodel_name='mlm.transaction', inverse_name='tran_invoice_id')
    is_invoice_of = fields.Selection(string="Is Invoice Of", selection=[('visit','Visits'),('bonus','RAP Bonus')])


    # def write(self, vals):
    #     result = super(AccountInvoiceInherit,self).write(vals)
    #     if self.ref:
    #         move_id = self.env["account.move"].sudo().search([("name","=",self.ref)])
    #         if self.invoice_payment_state == "paid":
    #
    #             if move_id.mlm_transaction_id:
    #                 move_id.mlm_transaction_id.write({"state":"paid"})
    #
    #     return result
