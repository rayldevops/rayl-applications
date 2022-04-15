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
from datetime import timedelta, date
import datetime
import json
import io
from odoo.tools import date_utils
import xlsxwriter
from odoo.tools.safe_eval import safe_eval

class AffiliateVisit(models.Model):
    _name = "affiliate.visit"
    _order = "create_date desc"
    _description = "Affiliate Visit Model"

    name = fields.Char(string = "Name",readonly='True')

    # @api.multi
    @api.depends('affiliate_type','type_id')
    def _calc_type_name(self):
        for record in self:
            if record.affiliate_type == 'product':
                record.type_name = record.env['product.template'].browse([record.type_id]).name
            if record.affiliate_type == 'category':
                record.type_name = record.env['product.public.category'].browse([record.type_id]).name
            if not record.type_name:
                record.type_name = ''


    affiliate_method = fields.Selection([("ppc","Pay Per Click"),("pps","Pay Per Sale")],string="Order Report",readonly='True',states={'draft': [('readonly', False)]},help="state of traffic either ppc or pps")
    affiliate_type = fields.Selection([("product","Product"),("category","Category")],string="Affiliate Type",readonly='True',states={'draft': [('readonly', False)]},help="whether the ppc or pps is on product or category")
    type_id = fields.Integer(String='Type Id',readonly='True',states={'draft': [('readonly', False)]},help="Id of product template on which ppc or pps traffic create")
    type_name = fields.Char(String='Type Name',readonly='True',states={'draft': [('readonly', False)]},compute='_calc_type_name',help="Name of the product")
    is_converted = fields.Boolean(string="Is Converted",readonly='True',states={'draft': [('readonly', False)]})
    sales_order_line_id = fields.Many2one("sale.order.line",readonly='True',states={'draft': [('readonly', False)]})
    affiliate_key = fields.Char(string="Key",readonly='True',states={'draft': [('readonly', False)]})
    affiliate_partner_id = fields.Many2one("res.partner",string="Affiliate",readonly='True',states={'draft': [('readonly', False)]})
    url = fields.Char(string="Url",readonly='True',states={'draft': [('readonly', False)]})
    ip_address = fields.Char(readonly='True',states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id,readonly='True',states={'draft': [('readonly', False)]})
    convert_date = fields.Datetime(string='Date',readonly='True',states={'draft': [('readonly', False)]})
    price_total = fields.Monetary(string="Sale value",related='sales_order_line_id.price_total',states={'draft': [('readonly', False)]},help="Total sale value of product" )
    unit_price = fields.Float(string="Product Unit Price", related='sales_order_line_id.price_unit', readonly='True',
                                  states={'draft': [('readonly', False)]},help="price unit of the product")
    commission_amt = fields.Float(readonly='True',states={'draft': [('readonly', False)]})
    affiliate_program_id = fields.Many2one('affiliate.program',string='Program',readonly='True',states={'draft': [('readonly', False)]})
    amt_type = fields.Char(string='Commission Matrix',readonly='True',states={'draft': [('readonly', False)]},help="Commission Matrix on which commission value calculated")
    act_invoice_id = fields.Many2one("account.move", string='Act Invoice id',readonly='True',states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancel'),
        ('confirm', 'Confirm'),
        ('invoice', 'Invoiced'),
        ('paid', 'Paid'),
        ], string='Status', readonly=True, default='draft' )
    product_quantity = fields.Integer(readonly='True',states={'draft': [('readonly', False)]})
    parent_affiliate_partner_id = fields.Many2one("res.partner",string=" Parent Affiliate",readonly='True',states={'draft': [('readonly', False)]})
    tier1 = fields.Boolean(string='Tier1')
    tier2 = fields.Boolean(string='Tier2')


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('affiliate.visit')
        new_visit =  super(AffiliateVisit,self).create(vals)
        return new_visit

# button on view action
    def action_cancel(self):
        self.state = 'cancel'
        return True

# button on view action
    def action_confirm(self):
        check_enable_ppc = self.env['res.config.settings'].sudo().website_constant().get('enable_ppc')

        if self.affiliate_method != 'ppc' and not self.sales_order_line_id:
            raise UserError("Order is not present in visit %s."%self.name)
        if self.affiliate_method != 'ppc' and not self.price_total:
            raise UserError("Sale value must be greater than zero.")

        if self.affiliate_method == 'ppc' and (not check_enable_ppc) :
            raise UserError("Pay per click is disable, so you can't confirm it's commission")
        self.state = 'confirm'
        status = self._get_rate(self.affiliate_method , self.affiliate_type, self.type_id )
        if status.get('is_error'):
            raise UserError(status['message'])
        #self.create_invoice()
        return True


# button on view action
    def action_paid(self):
        self.state = 'paid'
        return True



# scheduler according to the scheduler define in data automated scheduler

    @api.model
    def process_scheduler_queue(self):
        users_all = self.env['res.users'].search([('is_affiliate','=',True)])
        ConfigValues = self.env['res.config.settings'].sudo().website_constant()
        payment_day = ConfigValues.get('payment_day')
        threshold_amt = ConfigValues.get('minimum_amt')
        # make the date of current month of setting date
        payment_date = datetime.date(datetime.date.today().year, datetime.date.today().month, payment_day)
        for u in users_all:
            _logger.info("*****user-Name=%r******",u.name)
            visits = self.search([('state','=','confirm'),('affiliate_partner_id','=',u.partner_id.id)])
            _logger.info("*****user confirm  visits=%r******",visits)

            if payment_date and visits:
                visits = visits.filtered(lambda r: fields.Date.from_string(r.create_date) <= payment_date)
                _logger.info("*****filter- visits=%r******",visits)

            _logger.info("****before******before method***visits**%r*******",visits)
            visits = self.check_enable_ppc_visits(visits)
            # function to filter the visits if ppc is enable or disable accordingly
            _logger.info("*****after*****after method***visits**%r*******",visits)
            total_comm_per_user = 0
            if visits:
                for v in visits:
                    total_comm_per_user = total_comm_per_user + v.commission_amt
                if total_comm_per_user >= threshold_amt and payment_date:
                    _logger.info("*****user=%r*******create invoice of visits=%r***** invoice amount total commisiion=%r***",u.name,visits,total_comm_per_user)
                    _logger.info("===================fields.Datetime.now()=%r==================",fields.Datetime.now().date())
                    inv_id = self.env['account.move'].create({
                        'partner_id':u.partner_id.id,
                        'type':'in_invoice',
                        'invoice_date':fields.Datetime.now().date(),
                        })

                    dic={
                                'name':"Total earn commission on ppc and pps",
                                'quantity':1,
                                'price_unit':total_comm_per_user,
                                'move_id':inv_id.id,
                                'product_id':ConfigValues.get('aff_product_id'),
                            }
                    line = self.with_context({'journal_id':inv_id.journal_id.id}).env['account.move.line'].create(dic)
                    for v in visits:
                        v.state = 'invoice'
                        v.act_invoice_id = inv_id.id
        return True


    def check_enable_ppc_visits(self,visits):
        check_enable_ppc = self.env['res.config.settings'].sudo().website_constant().get('enable_ppc')
        if check_enable_ppc:
            return visits
        else:
            visits = visits.filtered(lambda v: v.affiliate_method == 'pps')
            return visits



    # method call from server action
    @api.model
    def create_invoice(self):
        # get the value of enable ppc from settings
        ConfigValues = self.env['res.config.settings'].sudo().website_constant()
        check_enable_ppc = ConfigValues.get('enable_ppc')
        aff_vst = self._context.get('active_ids') if self._context.get('active_ids') else [self.id]
        act_invoice = self.env['account.move']
        # check the first visit of context is ppc or pps and enable pps
        affiliate_method_type = self.browse([aff_vst[0]]).affiliate_method
        if affiliate_method_type == 'ppc' and (not check_enable_ppc) :
            raise UserError("Pay per click is disable, so you can't generate it's invoice")

        invoice_ids =[]
        for v in aff_vst:
            vst = self.browse([v])
             # [[0, 'virtual_754', {'sequence': 10, 'product_id': 36, 'name': '[Deposit] Deposit', 'account_id': 21, 'analytic_account_id': False, 'analytic_tag_ids': [[6, False, []]],
             #  'quantity': 1, 'product_uom_id': 1, 'price_unit': 150, 'discount': 0, 'tax_ids': [[6, False, [1]]]

            if vst.state == 'confirm':
                # ********** creating invoice line *********************
                if vst.sales_order_line_id:
                    dic={
                            'name':"Type "+vst.affiliate_type+" on Pay Per Sale ",
                            'quantity':1,
                            'price_unit':vst.commission_amt,
                            # 'move_id':inv_id.id,
                            # 'product_id':ConfigValues.get('aff_product_id'),
                        }
                else:
                    dic={
                            'name':"Type "+vst.affiliate_type+" on Pay Per Click ",
                            'price_unit':vst.commission_amt,
                            'quantity':1,
                            # 'product_id':ConfigValues.get('aff_product_id'),
                        }

                invoice_dict = [
                                { 
                                   'invoice_line_ids': [(0, 0, dic)],
                                   'move_type': 'in_invoice',
                                   # 'partner_id':vst.affiliate_partner_id.id,
                                   'partner_id':vst.parent_affiliate_partner_id.id,
                                   'invoice_date':fields.Datetime.now().date()
                                }]
                line = self.env['account.move'].create(invoice_dict)
                vst.state = 'invoice'
                vst.act_invoice_id = line.id
                invoice_ids.append(line)
                visit_obj = self.env['affiliate.visit'].sudo()
                # visit = visit_obj.create({
                #         'affiliate_method':'pps',
                #         'affiliate_key': vst.affiliate_partner_id.res_affiliate_key,
                #         'affiliate_partner_id': vst.affiliate_partner_id.id,
                #         'url':"",
                #         # 'ip_address':request.httprequest.environ['REMOTE_ADDR'],
                #         # 'type_id':product_tmpl_id,
                #         'affiliate_type': 'product',
                #         'type_name':s.product_id.id,
                #         'sales_order_line_id':s.id,
                #         'convert_date':fields.datetime.now(),
                #         'affiliate_program_id': partner_id.affiliate_program_id.id,
                #         'product_quantity' : s.product_uom_qty,
                #         'is_converted':True
                #       })
                vst.act_invoice_id.action_post()
        msg = str(len(invoice_ids))+' records has been invoiced out of '+str(len(aff_vst))
        partial_id = self.env['wk.wizard.message'].create({'text': msg})
        self.action_paid()
        return {
        'name': "Message",
        'view_mode': 'form',
        'view_id': False,
        'res_model': 'wk.wizard.message',
        'res_id': partial_id.id,
        'type': 'ir.actions.act_window',
        'nodestroy': True,
        'target': 'new',
        }


    def _get_rate(self,affiliate_method,affiliate_type,type_id):
        #_get_rate() methods arguments (pps,product,product_id) or (ppc,product,product_id) or (ppc,category,category_id)
        # check product.id in product.template
        # check category.id in product.public.category
        product_exists = False
        category_exists = False
        commission = 0.0
        commission_type = False
        adv_commision_amount = False
        response = {}
        if self.affiliate_program_id:
            if affiliate_type == 'product':
                product_exists = self.env['product.template'].browse([type_id])
            if affiliate_type == 'category':
                category_exists = self.env['product.public.category'].browse([type_id])

            if affiliate_method == 'ppc' and product_exists or category_exists: # pay per click
                commission = self.affiliate_program_id.amount_ppc_fixed
                commission_type = 'fixed'
                self.commission_amt = commission
            else:
                 # pay per sale
                if affiliate_method == 'pps' and product_exists :
                    #for pps_type simple
                    if self.affiliate_program_id.pps_type == 's':
                        if self.affiliate_program_id.matrix_type == 'f':  # fixed
                            commission =  self.commission_amt * self.product_quantity
                            commission_type = 'fixed'
                        else:
                            if self.affiliate_program_id.matrix_type == 'p' and (not self.commission_amt >100): # percentage
                                commission = (self.price_total * self.commission_amt/100)
                                commission_type = 'percentage'
                            else:
                                response={
                                        'is_error':1,
                                        'message':'Percenatge amount is greater than 100',
                                }
                    else:
                        # for pps type advance (advance depends upon price list)

                        if self.affiliate_program_id.pps_type == 'a' and product_exists:#for pps_type advance
                            adv_commision_amount,commission,commission_type = self.advance_pps_type_calc()
                            # adv_commision_amount = is a amount if advance commission
                            # commission = is a amount which is earned by commisiion
                            commission = commission * self.product_quantity
                            _logger.info("----commision_value-%r--------commision_value_type-%r------",commission,commission_type)
                            _logger.info('================advance_pps_type_calc===============')
                            if commission and commission_type:
                                _logger.info("---22----adv_commision_amount--%r--commision_value-%r--------commision_value_type-%r------",adv_commision_amount,commission,commission_type)

                            else:
                                response={
                                    'is_error':1,
                                    'message':'No commission Category Found for this product..'
                                }


                        else:
                            response={
                                    'is_error':1,
                                    'message':'pps_type is advance',
                            }

                else:
                    response={
                            'is_error':1,
                            'message':'Affilite method is niether ppc nor pps or affiliate type is absent(product or category)',
                    }
        else:

            response={
                    'is_error':1,
                    'message':'Program is absent in visit',
            }

        if commission:
            self.commission_amt = commission
            # self.amt_type = commission_type
            if commission_type == 'fixed' and affiliate_method == 'ppc':
                self.amt_type   =  self.currency_id.symbol+ str(self.affiliate_program_id.amount_ppc_fixed)
            if commission_type == 'percentage' and affiliate_method == 'ppc':
                self.amt_type =   str(self.affiliate_program_id.amount_ppc_fixed)+ '%'
            #for pps
            if commission_type == 'percentage' and self.affiliate_program_id.pps_type == 's':
                self.amt_type = str(self.commission_amt) +"%"
            if commission_type == 'fixed' and affiliate_method == 'pps' and self.affiliate_program_id.pps_type == 's':
                self.amt_type =    self.currency_id.symbol + str(self.commission_amt)
            if commission_type == 'fixed' and affiliate_method == 'pps' and self.affiliate_program_id.pps_type == 'a':
                self.amt_type =   self.currency_id.symbol + str(adv_commision_amount)+" advance"
            if commission_type == 'percentage' and affiliate_method == 'pps' and self.affiliate_program_id.pps_type == 'a':
                self.amt_type =   str(adv_commision_amount)+"%"+" advance"
            response={
                    'is_error':0,
                    'message':'Commission successfully added',
                    'comm_type':commission_type,
                    'comm_amt' : commission
            }

        else:
            if response.get('is_error') == 1:
                response={
                        'is_error':1,
                        'message':response.get('message'),
                }

        return response



    def advance_pps_type_calc(self):
        adv_commision_amount,commision_value,commision_value_type = self.env["advance.commision"].calc_commision_adv(self.affiliate_program_id.advance_commision_id.id, self.type_id , self.unit_price)
        # argument of calc_commision_adv(adv_comm_id, product_id on which commision apply , price of product)
        # return adv_commision_amount ,commision_value, commision_value_type
        _logger.info("---11----adv_commision_amount----commision_value-%r--------commision_value_type-%r------",adv_commision_amount,commision_value,commision_value_type)
        # return commision_value,commision_value_type
        return adv_commision_amount,commision_value,commision_value_type




    @api.model
    def process_ppc_maturity_scheduler_queue(self):
        _logger.info("-----Inside----process_ppc_maturity_scheduler_queue-----------")
        check_enable_ppc = self.env['res.config.settings'].sudo().website_constant().get('enable_ppc')
        all_ppc_visits = self.search([('affiliate_method','=','ppc'),('state','=','draft')])
        if check_enable_ppc:
            for visit in all_ppc_visits:
                visit.action_confirm()

    def action_reset_draft(self):
        self.write({'state': 'draft',
                    'act_invoice_id': False})


class AffiliateDailyReport(models.TransientModel):
    _name = "affiliate.daily.report"
    _description = "Affiliate Daily Report"

    def generate_daily_account_report(self):
        return self.env.ref('affiliate_management.daily_report_action_xls').report_action(self)

class ClientScopeXlsx(models.AbstractModel):
    _name = 'report.daily_report_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, product):
        worksheet = workbook.add_worksheet()
        format = workbook.add_format({'num_format': 'dd/mm/YYYY', 'align': 'left', 'valign': 'vcenter'})
        title_format = workbook.add_format({
            'font_size': 10,
            'border': 5,
            'align': 'left',
            'bg_color': '#ccccff',
            'valign': 'vcenter'})
        output_format = workbook.add_format({
            'font_size': 10,
            'border': 1,
            'align': 'left',
            'valign': 'vcenter'})
        header_format = workbook.add_format({
            'font_size': 14,
            'border': 5,
            'align': 'center',
            'valign': 'vcenter'})
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 10)
        worksheet.merge_range('C3:H4', 'Daily Account Report ' +str(date.today()) , header_format)
        worksheet.write('A6', 'Serial No.', title_format)
        worksheet.write('B6', 'subscriber/customer Name', title_format)
        worksheet.write('C6', 'Plan Amount', title_format)
        worksheet.write('D6', 'Active', title_format)
        row = 6
        col = 0
        sr_no = 1
        today = fields.Datetime.today()
        sale_obj = self.env['sale.order'].sudo().search([('create_date', '>=', today),
                                                         ("amount_total","in",[59.95,19.95])])
        for order in sale_obj:
            worksheet.write(row, col, sr_no or ' ', output_format)
            worksheet.write(row, col + 1, order.partner_id.name or ' ', output_format)
            worksheet.write(row, col + 2, order.amount_total or ' ', output_format)
            worksheet.write(row, col + 3, 'Yes', output_format)
            row = row + 1
            sr_no = sr_no + 1