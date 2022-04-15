from odoo import api, fields, models, tools, _
from odoo.tools.misc import xlsxwriter
from odoo.tools import pycompat
from odoo.tools import date_utils
import io
import json


class CommissionPayout(models.Model):
    _inherit = 'affiliate.visit'

    payout_no = fields.Integer(default=0)

    # name = fields.Char('Name') example

    def action_export_data(self):

        self.env.cr.execute("""Select 
                res_currency.name,
                SUM(affiliate_visit.commission_amt) as total_commission_amt,
                res_partner.name,
                res_partner.street as street,
                res_partner.city,
                res_country_state.name,
                res_country.name,
                res_partner.zip,
                affiliate_program.name,
                CASE WHEN ps.institution_number != 0 THEN ps.institution_number ELSE bd.institution_number END as bank_institution_number,
                ps.branch_transit_number,
                ps.bank_account_number
                from affiliate_visit
                left join res_partner on affiliate_visit.parent_affiliate_partner_id = res_partner.id 
                left join res_users as rs on rs.partner_id = res_partner.id 
                left join default_payout_account on default_payout_account.user_id = rs.id
                left join payout_setting as ps on ps.id = default_payout_account.default_payout_id 
                left join res_currency on res_currency.id = affiliate_visit.currency_id 
                left join res_country on res_country.id = res_partner.country_id
                left join res_country_state on res_country_state.id = res_partner.state_id
                left join bank_details as bd on ps.bank_id = bd.id 
                left join affiliate_program on affiliate_program.id = affiliate_visit.affiliate_program_id
                WHERE affiliate_visit.id IN %(ids)s group by affiliate_visit.parent_affiliate_partner_id, res_currency.name, res_partner.name, res_partner.city, res_partner.street, res_country_state.name,
                res_country.name,
                res_partner.zip,
                affiliate_program.name,
                ps.institution_number,
                bd.institution_number,
                ps.branch_transit_number,
                ps.bank_account_number order by affiliate_visit.parent_affiliate_partner_id desc""",
                            {'ids': tuple(self.ids)})
        account_details = self.env.cr.fetchall()
        self.env.cr.execute('select max(payout_no) from affiliate_visit')
        lst_batch_no = self.env.cr.fetchall()
        batch_no = 0
        if lst_batch_no[0]:
            batch_no = lst_batch_no[0][0]
            self.write({'payout_no': batch_no + 1})
            for i in self.ids:
                inv = self.browse([i])
                inv.action_confirm()
        return {
            # 'type': 'ir_actions_xlsx_download',
            'data': {'model': 'affiliate.visit',
                     'options': json.dumps(account_details, default=date_utils.json_default),
                     'output_format': 'csv',
                     'report_name': 'Csv Report',
                     },
            'report_type': 'csv',
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
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

    def get_csv_report(self, rows):
        output = io.BytesIO()
        writer = pycompat.csv_writer(output, quoting=1)
        fields = ['Service', 'Currency', 'Amount', 'Beneficiary', 'Address', 'City', 'Province', 'Country',
                  'Postal Code', 'Client Reference Number', 'Institution Number', 'Transit Number', 'Account Number']
        writer.writerow(fields)
        for data in rows:
            row = []
            row.append('Debit')
            for d in data:
                # Spreadsheet apps tend to detect formulas on leading =, + and -
                if isinstance(d, str) and d.startswith(('=', '-', '+')):
                    d = "'" + d

                row.append(pycompat.to_text(d))
            writer.writerow(row)
        return output.getvalue()
