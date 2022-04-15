from odoo import api, fields, models, tools, _


class PayoutSetting(models.Model):
    _name = 'payout.setting'

    name = fields.Char('Name')
    user_id = fields.Many2one('res.users','User Id',default=lambda self: self.env.user)
    bank_id = fields.Many2one('bank.details',"Bank ID")
    other_bank_name = fields.Char("Other Bank Name")
    bank_name = fields.Char('Bank Name',related='bank_id.bank_name')
    branch_transit_number = fields.Char("Branch Transit Number")
    bank_account_number = fields.Char("Bank Account Number")
    confirm_bank_account_number = fields.Char("Confirm Bank Account Number")
    payment_option = fields.Selection([('electronic_funds_transfer', 'electronic funds transfer'),
                                       ('credit_card', 'credit card')], string='Payment Option')
    mask_bank_account_number = fields.Char('Mask Bank Account Number')
    default_payout_id = fields.One2many('default.payout.account', 'default_payout_id', string="Default")
    institution_number = fields.Integer("Institution Number")
    institution_number_bank_details = fields.Integer('Institution Number', related='bank_id.institution_number')
    compute_bank_name = fields.Char(compute='_compute_bank_name',string="Bank Name")

    bank_account_type = fields.Char("Bank Account Type")
    company_name = fields.Char("Company Name")

    def _compute_institution_number(self):
        for rec in self:
            if rec.other_bank_name:
                rec.compute_institution_number = rec.institution_number
            else:
                rec.compute_institution_number = rec.institution_number_bank_details


    compute_institution_number = fields.Char(compute='_compute_institution_number',string="Institution Number")

    def _compute_bank_name(self):
        for rec in self:
            if rec.other_bank_name:
                rec.compute_bank_name = rec.other_bank_name
            else:
                rec.compute_bank_name = rec.bank_id.bank_name

    def get_current_payout(self):
        for rec in self:
            user_id = rec.user_id.id
            payout_id = rec.id
            payout_rec = self.env['default.payout.account'].sudo().search([('user_id', '=', user_id)])
            if payout_rec.default_payout_id.id == payout_id:
                rec.is_default = True
            else:
                rec.is_default = False

    is_default = fields.Boolean(string='Check default Payout', compute='get_current_payout')

    def set_bank_default(self):
        for rec in self:
            user_id = rec.user_id.id
            payout_rec = self.env['default.payout.account'].sudo().search([('user_id', '=', user_id)])
            if payout_rec:
                default_obj = self.env['default.payout.account'].sudo().search(
                    [('user_id', '=', user_id)]).write({
                    'default_payout_id': rec.id,
                })
            else:
                default_obj = self.env['default.payout.account'].sudo().create({
                    'user_id': user_id,
                    'default_payout_id': rec.id,
                })


class BankDetails(models.Model):
    _name = 'bank.details'
    _rec_name = 'bank_name'

    bank_name = fields.Char("Bank Name")
    institution_number = fields.Integer("Institution Number")
    branch_transit_id = fields.One2many('branch.transit', 'bank_id', string="Branch Transit")


class BranchTransit(models.Model):
    _name = 'branch.transit'

    transit_number = fields.Char("Transit Number")
    bank_id = fields.Many2one('bank.details',"Bank ID")
    address1 = fields.Char("Branch Address1")
    address2 = fields.Char("Branch Address2")
    city = fields.Char("Branch City")
    province = fields.Char("Branch Province")
    postal_code = fields.Char("Branch Postal Code")

class DefaultAccount(models.Model):
    _name = 'default.payout.account'

    user_id = fields.Many2one('res.users', 'User Id', default=lambda self: self.env.user)
    default_payout_id = fields.Many2one('payout.setting','Default')
