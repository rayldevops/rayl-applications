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
from odoo.http import request
from datetime import timedelta
import datetime

class AccountInvoiceInherit(models.Model):
    _inherit = 'account.move'

    aff_visit_id = fields.One2many('affiliate.visit','act_invoice_id',string="Report")

    def action_post(self):
        res = super(AccountInvoiceInherit, self).action_post()
        visit_obj = self.env['affiliate.visit'].sudo().search([('affiliate_partner_id', '=', self.partner_id.id)], limit=1)
        if visit_obj:
            visit = visit_obj.write({'state': 'invoice'})
        return res

    # def action_register_payment(self):
    #     res = super(AccountInvoiceInherit, self).action_register_payment()
    #     visit_obj = self.env['affiliate.visit'].sudo().search([('affiliate_partner_id', '=', self.partner_id.id)], limit=1)
    #     if visit_obj:
    #         visit = visit_obj.write({'state': 'paid'})
    #     return res

        # Automate Stripe Payments
    #@api.model
    def automate_stripe_scheduler(self):
        #users_all = self.env['res.users'].search([('is_affiliate', '=', True),('id','=',299)])
        users_all = self.env['res.users'].search([('is_affiliate', '=', True),('id','=',324)])
        #users_all = self.env['res.users'].search([('is_affiliate', '=', True),('id','=',328)])
        payment_day = 30
        payment_date = datetime.date(datetime.date.today().year, datetime.date.today().month, payment_day)
        for u in users_all:
            data = self.search([('state', '=', 'confirm')])
            visits = self.search([('state', '=', 'confirm'), ('affiliate_partner_id', '=', u.partner_id.id)])
            if visits:
                visits = visits.filtered(lambda r: fields.Date.from_string(r.create_date) == payment_date)


class SaleAdvancePaymentInvInherits(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _create_invoice(self):
        res = super(SaleAdvancePaymentInvInherits, self)._create_invoice()
        visit_obj = self.env['affiliate.visit'].sudo()
        visit = visit_obj.create({
            'affiliate_method': 'pps',
            'affiliate_key': vst.affiliate_partner_id.res_affiliate_key,
            'affiliate_partner_id': vst.affiliate_partner_id.id,
            'url': "",
            # 'ip_address':request.httprequest.environ['REMOTE_ADDR'],
            # 'type_id':product_tmpl_id,
            'affiliate_type': 'product',
            'type_name': s.product_id.id,
            'sales_order_line_id': s.id,
            'convert_date': fields.datetime.now(),
            'affiliate_program_id': partner_id.affiliate_program_id.id,
            'product_quantity': s.product_uom_qty,
            'is_converted': True
        })
        return res

#     def write(self, vals):
#         result = super(AccountInvoiceInherit,self).write(vals)
#         if self.ref:
#             move_id = self.env["account.move"].sudo().search([("name","=",self.ref)])
#             if self.payment_state == "paid":

#                 if move_id.aff_visit_id:
#                     move_id.aff_visit_id.write({"state":"paid"})

#         return result

class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'
    _description = "Account Payment Inherit Model"


    # def action_validate_invoice_payment(self):
    def post(self):
        result = super(AccountPaymentInherit,self).post()
        if result and self.invoice_ids:
            move_id = self.invoice_ids[0]
            if move_id.payment_state == "paid" and move_id.aff_visit_id and move_id.aff_visit_id.state != "paid":
                move_id.aff_visit_id.write({"state":"paid"})

        return result
