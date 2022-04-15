from odoo import models, fields, api
from odoo.exceptions import ValidationError


class wizard_invite_user(models.TransientModel):
    _name = 'invite.user'

    participant_ids = fields.Many2many('res.users', 'res_company_participants_rel', 'cid', 'participant_id', string='Users')



    # @api.multi
    # def partially_pay(self):
    #     """
    #     @param self: The object pointer
    #     """
    #     for rec in self:
    #         data = self.env.context.get('active_ids')
    #         tenancy_ids = self.env['tenancy.rent.schedule'].browse(data)
    #         partial_amount=rec.pay_amount
    #         check_amount_val=rec.check_rem_amount
    #         if partial_amount > check_amount_val and check_amount_val != 0:
    #             raise ValidationError(('The partial amount should not be greater then remaining amount'))
    #         journal_id = rec.payment_method
    #         created_move_ids = []
    #         journal_ids = self.env['account.journal'].search([('name', 'like', 'Rent Cash')])
    #         payment_methods = journal_ids[0].inbound_payment_method_ids or journal_ids[0].outbound_payment_method_ids
    #         payment_method_id = payment_methods and payment_methods[0] or False
    #         for tenancy_rec in tenancy_ids:
    #             amount = tenancy_rec.amount
    #             if tenancy_rec.discount_move_id:
    #                 if tenancy_rec.discount_type == 'fixed':
    #                     amount = tenancy_rec.amount - tenancy_rec.discount
    #                 else:
    #                     amount = tenancy_rec.amount - tenancy_rec.tenancy_id.rent * tenancy_rec.discount / 100
    #             if tenancy_rec.legal_move_id:
    #                 amount = amount - tenancy_rec.legal_charges
    #             remain_amount = amount - partial_amount
    #             if tenancy_rec.remaining_amount:
    #                 remain_amount = tenancy_rec.remaining_amount - partial_amount
    #
    #             move_vals = {
    #                 'partner_id': tenancy_rec.tenancy_id.tenant_id.parent_id.id,
    #                 'payment_method_id': payment_method_id.id,
    #                 'partner_type': 'customer',
    #                 'journal_id': journal_id.id or journal_ids[0].id,
    #                 'payment_type': 'inbound',
    #                 'communication': 'Rent Received',
    #                 'tenancy_id': tenancy_rec.tenancy_id.id,
    #                 'amount': partial_amount,
    #                 'property_id': tenancy_rec.tenancy_id.property_id.id,
    #                 'portfolio_id': tenancy_rec.tenancy_id.wallet_id.id,
    #                 'property_ids': [(6, 0, tenancy_rec.property_ids.ids)],
    #             }
    #             paid_id = self.env['account.payment'].create(move_vals)
    #             paid_id.post()
    #             account_obj = self.env['account.analytic.account'].search(
    #                 [('name', 'ilike', 'Portfolio ' + str(paid_id.portfolio_id.name))])
    #             paid_id.move_line_ids.write({'analytic_account_id': account_obj[0].id})
    #             tenancy_rec.write({'partial_paid': True,'remaining_amount':remain_amount,'cust_payment_ids': [(4, paid_id.id, None)]})
    #             # created_move_ids.append(paid_id.id)
    #         context = dict(self._context or {})
    #         acc_pay_form_id = self.env['ir.model.data'].get_object_reference('account', 'view_account_payment_form')[1]
    #         return {
    #             'view_type': 'form',
    #             'view_id': acc_pay_form_id,
    #             'view_mode': 'form',
    #             'res_model': 'account.payment',
    #             'res_id': paid_id.id,
    #             'type': 'ir.actions.act_window',
    #             'target': 'current',
    #             'context': context,
    #         }
