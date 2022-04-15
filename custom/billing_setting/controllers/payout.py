from odoo import fields, models, http, _
from odoo.http import request
from odoo.addons.base.models.ir_ui_view import keep_query
import odoo
import re
import werkzeug
from lxml import etree
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError, AccessDenied
import stripe


class PayoutAccounts(http.Controller):

    @http.route(['/my/payout'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def my_payout(self, **kw):

        error = dict()
        error_message = []
        errors = {}
        if kw.get('error'):
            error_message.append(_(kw.get('error')))

        message = dict()
        success_message = []
        messages = {}
        if kw.get('message'):
            success_message.append(_(kw.get('message')))

        pay_details = request.env['bank.details'].sudo().search([])

        errors['error_message'] = error_message
        messages['success_message'] = success_message
        return request.render("billing_setting.payout_setting_form", {'values': pay_details,
                                                                      'error': errors,
                                                                      'message': messages,
                                                                      })

    @http.route('/payout/account', type='http', methods=['GET', 'POST'], auth="public", website=True)
    def my_payout_account(self, **kw):
        error = dict()
        error_message = []
        errors = {}
        if kw.get('error'):
            error_message.append(_(kw.get('error')))

        message = dict()
        success_message = []
        messages = {}
        if kw.get('message'):
            success_message.append(_(kw.get('message')))


        user_id = http.request.env.context.get('uid')
        payout_details = request.env['payout.setting'].sudo().search([('user_id', '=', user_id)])

        errors['error_message'] = error_message
        messages['success_message'] = success_message
        return request.render("billing_setting.payout_account_list", {'payout_details': payout_details,
                                                                      'error': errors,
                                                                      'message': messages,
                                                                      })

    @http.route('/my/payout/submit', type='http', auth="public", website=True)
    def payout_form_submit(self, *args, **post):
        if post:
            digits_to_keep = 4
            mask_char = '#'
            acc_number = post.get('bank_account_number')
            num_of_digits = sum(map(str.isdigit, acc_number))
            digits_to_mask = num_of_digits - digits_to_keep
            masked_string = re.sub('\d', mask_char, acc_number, digits_to_mask)

            if post.get('payment_option') == 'electronic_funds_transfer':
                if post.get('bank_account_number') != post.get('confirm_bank_account_number'):
                    return request.redirect('/my/payout/?error=Please Check your Details and Try again')
                else:
                    payout = request.env['payout.setting'].sudo().create({
                        'bank_id': post.get('bank_id'),
                        'other_bank_name': post.get('other_bank_name'),
                        'payment_option': post.get('payment_option'),
                        'branch_transit_number': post.get('branch_transit_number'),
                        'bank_account_number': post.get('bank_account_number'),
                        'mask_bank_account_number': masked_string,
                        'confirm_bank_account_number': post.get('confirm_bank_account_number'),
                        'bank_account_type': post.get('bank_account_type'),
                        'company_name': post.get('company_name'),
                    })
                    if payout:
                        user_id = http.request.env.context.get('uid')
                        payout_rec = request.env['default.payout.account'].sudo().search([('user_id', '=', user_id)])
                        if payout_rec:
                            default_obj = request.env['default.payout.account'].sudo().search(
                                [('user_id', '=', user_id)]).write({
                                'default_payout_id': payout.id,
                            })
                        else:
                            default_obj = request.env['default.payout.account'].sudo().create({
                                'default_payout_id': payout.id,
                            })
                        return request.redirect('/payout/account/?message=Data Updated Successfully')
                        #return werkzeug.utils.redirect("/my/payout/?message=Data Updated Successfully")
                    else:
                        return request.redirect('/my/payout/?error=Please Check your Details and Try again')
            else:
                return request.redirect('/my/payout/?error=Please Check your Details and Try again')
        else:
            return request.redirect('/my/payout/?error=Please Check your Details and Try again')

    @http.route('/remove/payout/bank', type='http', auth="public", website=True)
    def remove_payout_account(self, **post):
        payout_id = post.get('payout_setting_id')
        payout_obj = request.env['payout.setting'].sudo().search([('id', '=', payout_id)])
        payout_obj.unlink()
        return werkzeug.utils.redirect("/payout/account")

    @http.route(['/bank_transit'], type='json', methods=['POST'], auth="public", website=True)
    def bank_transit(self, id, **kw):
        branch_transit = request.env['branch.transit'].sudo().search([('bank_id', '=', int(id))])
        res = []
        for row in branch_transit:
            res.append({'id': row.id,
                        'transit_number': row.transit_number,
                        'address_string': "{0} {1} {2}". format(row.address1 if row.address1 else '', row.address2  if row.address2 else '', row.city if row.city else '')
                        })
        return res

    @http.route('/set_default/payout/bank', type='http', auth="public", website=True)
    def set_payout_default_account(self, **post):
        user_id = http.request.env.context.get('uid')
        payout_id = post.get('payout_setting_id')
        payout_rec = request.env['default.payout.account'].sudo().search([('user_id', '=', user_id)])
        if payout_rec:
            default_obj = request.env['default.payout.account'].sudo().search([('user_id', '=', user_id)]).write({
                'default_payout_id': payout_id,
            })
        else:
            default_obj = request.env['default.payout.account'].sudo().create({
                'default_payout_id': payout_id,
            })
        return werkzeug.utils.redirect("/payout/account")
