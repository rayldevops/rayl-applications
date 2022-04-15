from odoo import api, fields, models, tools, _
from odoo.tools.misc import xlsxwriter
import base64
from odoo.tools import date_utils
import io
import json


class AccountMove(models.Model):
    _inherit = 'account.move'

    commission_amount = fields.Float(related='aff_visit_id.commission_amt')
    # contract_template = fields.Binary('Template', compute="_get_template")
    carrier_xlsx_document = fields.Binary('Account File', readonly=True, attachment=False)
    carrier_xlsx_document_name = fields.Char(string='Filename')
    commission_status = fields.Selection([
        ('to_be_process', 'To Be Process'),
        ('processing', 'Processing'),
        ('complete', 'Complete')], 'Commission Status', default='to_be_process')

    def action_to_be_process(self):
        self.write({'commission_status': 'to_be_process'})

    def action_processing(self):
        self.write({'commission_status': 'processing'})

    def mark_done(self):
        self.write({'commission_status': 'complete'})

    # def action_complete(self):
    #     self.write({'commission_status': 'complete'})

    # def action_export_data(self):
    #     account_details = self.env['account.move'].search([('id', 'in', self.ids)])
    #     # for vals in account_details.partner_id:
    #     file_name = 'temp'
    #     output = io.BytesIO()
    #     workbook = xlsxwriter.Workbook(file_name, {'in_memory': True})
    #     worksheet = workbook.add_worksheet()
    #     headers = [('Content-Type', 'application/vnd.ms-excel'),
    #                ('Content-Disposition', content_disposition(file_name + '.xlsx'))]
    #     worksheet.set_header(headers)
    #     # header = ['Address']
    #     row = 0
    #     col = 0
    #     for e in header:
    #         worksheet.write(row, col, e)
    #         col += 1
    #     row += 1
    #     for vals in account_details.partner_id:
    #         worksheet.write(row, 0, vals.street)
    #     workbook.close()
    #     output.seek(0)
    #     response.stream.write(output.read())
    #     output.close()
    #     with open(file_name, "w") as file:
    #         file.writerow(worksheet)
    # file.read()
    # file_base64 = base64.b64encode(file.read())
    # self.carrier_xlsx_document_name = self.name + '.xlsx'
    # self.write({'carrier_xlsx_document': file_base64, })
    #
    def action_export_data(self):
        # account_details = self.env['account.move'].search([('id', 'in', self.ids)])
        # user_id = self.env['res.users'].search([])
        # maxi = user_id.mapped('max')
        # wt = self.env['account.move']
        # partner_id = wt.search([('id', 'in', self.ids)]).partner_id
        # user_id = wt.search([('id', 'in', self.ids)]).user_id
        # partner_id = wt.browse(partner_id)
        # user_id = wt.browse(user_id)
        # res.partner = street,country_id,currency_id,state_id,city,zip

        self.env.cr.execute("""Select 
        res_currency.name,
        affiliate_visit.commission_amt,
        res_partner.name,
        res_partner.street as street,
        res_partner.city,
        res_country_state.name,
        res_country.name,
        res_partner.zip,
        affiliate_program.name,
        bd.institution_number,
        ps.branch_transit_number,
        ps.bank_account_number 
        from account_move
        left join res_partner on account_move.partner_id = res_partner.id 
        left join res_users as rs on rs.id = res_partner.user_id 
        left join payout_setting as ps on ps.user_id = rs.id 
        left join res_currency on res_currency.id = account_move.currency_id 
        left join res_country on res_country.id = res_partner.country_id
        left join res_country_state on res_country_state.id = res_partner.state_id
        left join bank_details as bd on ps.bank_id = bd.id 
        left join account_move_line on account_move_line.move_id = account_move.id
        join affiliate_visit on account_move.id = affiliate_visit.act_invoice_id
        left join affiliate_program on affiliate_program.id = affiliate_visit.affiliate_program_id
        WHERE account_move.id IN %(ids)s order by account_move.id desc""",{'ids': tuple(self.ids)})
        account_details = self.env.cr.fetchall()
        # list_fields = ['street', 'name']
        # list_street = []
        self.write({'commission_status': 'processing'})
        data = []
        # data2 = {}
        # for vals in account_details:
        #     # for field in list_fields:
        #     for each in vals:
        #         data.append(each)
        #     data2.update({data})
        return {
            # 'type': 'ir_actions_xlsx_download',
            'data': {'model': 'account.move',
                     'options': json.dumps(account_details, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Excel Report',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format({'font_size': '12px'})
        head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '20px'})
        txt = workbook.add_format({'font_size': '10px'})
        # sheet.merge_range('B2:I3', 'EXCEL REPORT', head)
        # sheet.write(1, 0, obj.timesheet_ids.date[0], bold)
        sheet.write('A1', 'Service', cell_format)
        sheet.write('B1', 'Currency', cell_format)
        sheet.write('C1', 'Amount', cell_format)
        sheet.write('D1', 'Beneficiary Full Name', cell_format)
        sheet.write('E1', 'Address', cell_format)
        sheet.write('F1', 'City', cell_format)
        sheet.write('G1', 'Province', cell_format)
        sheet.write('H1', 'Country', cell_format)
        sheet.write('I1', 'Postal Code', cell_format)
        sheet.write('J1', 'Client Reference Number', cell_format)
        sheet.write('K1', 'Institution Number', cell_format)
        sheet.write('L1', 'Transit Number', cell_format)
        sheet.write('M1', 'Account Number', cell_format)
        # sheet.write(1, 0, 'Debit')
        i = 1
        for each in data:
            sheet.write(i, 0, 'Debit')
            sheet.write_row(i, 1, each)
            i += 1
        # sheet.write_column(1, 1, data['display_name'])
        # sheet.write_column(1,2, data2['street'])
        # sheet.write_column(1,3, data2['street'])
        # sheet.write_column(1,4, data2['street'])
        # sheet.write_column(1, 5, data2['city'])
        # sheet.write_column(1, 6, data2['state_id'])
        # sheet.write_column(1, 7, data2['country_id'])
        # sheet.write_column(1,8, data2['street'])
        # sheet.write_column(1,9, data2['street'])
        # sheet.write_column(1,10, data2['street'])
        # sheet.write_column(1,11, data2['street'])
        # sheet.write('F6', 'To:', cell_format)
        # sheet.merge_range('G6:H6', data['end_date'], txt)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()


class CommissionListing(models.Model):
    _name = 'commission.listing'

    name = fields.Char('Name')


class Users(models.Model):
    _inherit = 'res.users'

    billing_ids = fields.One2many('billing.setting', 'user_id')