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

from odoo import api, fields, models, exceptions, _
from odoo import SUPERUSER_ID
from odoo.addons import base
from datetime import datetime



class AffiliateProgramInherit(models.Model):
    _inherit = 'affiliate.program'

    @api.depends('level_commission_ids')
    def _check_level_commission_depth(self):
        self.level_depth = len(self.level_commission_ids)

    insertion_type = fields.Selection(string="Insertion Type", selection=[('loi','Level Order Insertion'),('poi','Parent Order Insertion')])
    mlm_membership_product = fields.Many2one(string="RAP Membership", comodel_name="product.template")
    upgrade_membership_product = fields.Many2one(string="RAP Upgrade Membership", comodel_name="product.template")
    bundle_membership_product = fields.Many2one(string="RAP Bundle Membership", comodel_name="product.template")
    root = fields.Many2one(string="Root", comodel_name = "res.partner", domain="[('is_affiliate','=',True),('bought_membership','=',True),('is_dispute','=',False)]")
    previous_mlm_product = fields.Many2one(string="Previous RAP Product",comodel_name="product.product")

    allow_fcb_bonus = fields.Boolean("FCB Bonus")
    fcb_matrix_type = fields.Selection([("f","Fixed"),("p","Percentage")],required=True,default='f',string="Matrix Type")
    fcb_bonus_amount = fields.Float(string="Amount")
    level_commission_ids = fields.One2many(string="Level Commissions",comodel_name="level.commission",inverse_name = "aff_prg")
    level_depth = fields.Integer(compute=_check_level_commission_depth)
    allow_lcb_bonus = fields.Boolean("LCB Bonus")
    lcb_matrix_type = fields.Selection([("f","Fixed"),("p","Percentage")],required=True,default='f',string="Matrix Type")
    level_bonus_amount = fields.Float(string="Amount")

    bonus_schedule = fields.Many2one(string="Bonus Schedule", comodel_name="ir.cron")

    mlm_work_title = fields.Text(string="How RAP Works Title", translate=True)
    mlm_work_text = fields.Html(string="How RAP Works Text", translate=True)
    about_ref_code = fields.Html(string="About Referral Code", translate= True)

    def get_mlm_configuration(self):
        id = self.search([],limit=1)
        return {
        "insertion_type": id.insertion_type,
        "mlm_membership_product": id.mlm_membership_product,
        "upgrade_membership_product":id.upgrade_membership_product,
        "bundle_membership_product":id.bundle_membership_product,
        "root":id.root,
        "first_child_bonus_amount": id.fcb_bonus_amount,
        "level_bonus_amount": id.level_bonus_amount,
        "bonus_schedule": id.bonus_schedule,
        "mlm_work_title": id.mlm_work_title,
        "mlm_work_text": id.mlm_work_text,
        "about_ref_code": id.about_ref_code,
        "allow_fcb_bonus": id.allow_fcb_bonus,
        "allow_lcb_bonus": id.allow_lcb_bonus,
        # "level_commission_ids": [level_commission_id for level_commission_id in id.level_commission_ids][::-1],
        "level_commission_ids":{level_commission_id.level: level_commission_id for level_commission_id in id.level_commission_ids},
        "level_depth": id.level_depth,
        "fcb_matrix_type": id.fcb_matrix_type,
        "lcb_matrix_type": id.lcb_matrix_type,
        }



    @api.model
    def set_admin_affiliate(self):
        admin = self.env.ref('base.partner_admin')
        # admin = self.env['res.users'].browse(SUPERUSER_ID).partner_id
        admin.is_affiliate = True
        admin.bought_membership = True
        admin.affiliate_program_id = self.env['affiliate.program'].search([])[-1].id
        admin.generate_key()

    @api.onchange('insertion_type')
    def set_root(self):
        if self.insertion_type == 'loi':
            # admin = self.env['res.users'].browse(SUPERUSER_ID).partner_id
            admin = self.env.ref('base.partner_admin').id
            self.root = admin

    def write(self,vals):
        raise_exception = False
        if vals.get('fcb_bonus_amount') or vals.get('fcb_matrix_type'):
            if vals.get('fcb_matrix_type') == 'p' and vals.get('fcb_bonus_amount',0) > 100:
                raise_exception = True
            elif vals.get('fcb_bonus_amount',0) > 100 and vals.get('fcb_matrix_type') != 'f' and self.fcb_matrix_type == 'p':
                raise_exception = True
            elif vals.get('fcb_matrix_type') == 'p' and not vals.get('fcb_bonus_amount', self.fcb_bonus_amount) <= 100 and self.fcb_bonus_amount > 100:
                raise_exception = True


        if vals.get('level_bonus_amount') or vals.get('lcb_matrix_type'):
            if vals.get('lcb_matrix_type') == 'p' and vals.get('level_bonus_amount',0) > 100:
                raise_exception = True
            elif vals.get('level_bonus_amount',0) > 100 and vals.get('lcb_matrix_type') != 'f' and self.lcb_matrix_type == 'p':
                raise_exception = True
            elif vals.get('lcb_matrix_type') == 'p' and not vals.get('level_bonus_amount', self.level_bonus_amount) <= 100 and self.level_bonus_amount > 100:
                raise_exception = True

        if raise_exception:
            raise exceptions.UserError(_('Percentage amount cannot be greater than 100'))

        result = super(models.Model,self).write(vals)
        if vals.get('mlm_membership_product'):
            mlm_membership_product = self.get_mlm_configuration().get('mlm_membership_product').product_variant_id
            mlm_membership_product.is_mlm_product = True
            if self.previous_mlm_product:
                self.previous_mlm_product.is_mlm_product = False
            self.previous_mlm_product = mlm_membership_product
        return result

    @api.model
    def set_default_mlm_configuration(self):
        program = self.env['affiliate.program'].sudo().search([],limit=1)
        program.bonus_schedule = self.env.ref('affiliate_management_mlm.ir_cron_scheduler_mlm_bonus_action')
        program.mlm_membership_product = self.env.ref('affiliate_management_mlm.product_template_mlm_membership')
        # program.root = self.env['res.users'].browse(SUPERUSER_ID).partner_id
        program.root = self.env.ref('base.partner_admin').id
        level_commissions = self.env['level.commission'].sudo().search([])
        for level_commission in level_commissions:
            level_commission.aff_prg = program.id
        program.mlm_work_title = """The process is very simple. Simply, enroll into Affiliate Program and buy the Multi Level Marketing Membership, share your Affiliate Referral code with others and make them your members and get bonus for your first child and level completion, as :"""
        program.mlm_work_text = """<ol><li><p style='text-align: left; margin-left: 3em;'>Referral code submitted at the time of signup or after login will be authenticated.</p></li><li><p style='text-align: left; margin-left: 3em;'>Referral code is considered valid if the Affiliate whose Referral code is provided has bought the Multi Level Membership.</p></li><li><p style='text-align: left; margin-left: 3em;'>Referring Affiliate also have to buy the Multi Level Marketing Membership.</p></li><li><p style='text-align: left; margin-left: 3em;'>After buying the membership he/she will become a Multi Level Marketing Member.</p></li><li><p style='text-align: left; margin-left: 3em;'>A bonus will be provided to you if its your first member and if you have completed a Level by making Two Members.</p></li><li><p style='text-align: left; margin-left: 3em;'>As your members will grow you will be provided with more level completion bonuses.</p></li></ol>"""
        program.about_ref_code = """Referral code is shared by the Multi Level Marketing member affiliate and the referral code would be used to make you a Multi Level Marketing member of the referenced affiliate."""

    def transaction_invoice_scheduler(self):

        aff_ids = self.env['res.partner'].sudo().search([('is_affiliate','=',True),('bought_membership','=', True),('transaction_ids','!=', False)])
        ConfigValues = self.env['res.config.settings'].sudo().website_constant()

        for aff_id in aff_ids:

            transactions = aff_id.transaction_ids
            appr_transactions = transactions.filtered(lambda tran: tran.state == 'approve')

            if appr_transactions:
                line_vals = []
                for appr_transaction in appr_transactions:


                    line_vals.append((0,0,{
                        'name':"Total bonus earned on First Child" if appr_transaction.bonus_type == 'fcb' else "Total bonus earned on Level Completion",
                        'quantity':1,
                        'price_unit':appr_transaction.credit,
                        'product_id':ConfigValues.get('aff_product_id'),
                        }))

                move_id = self.env['account.move'].create({
                            'partner_id': aff_id.id,
                            'move_type':'in_invoice',
                            # 'invoice_date':str(fields.Datetime.now()),
                            'is_invoice_of': 'bonus',
                            'invoice_line_ids': line_vals,
                            })

                appr_transactions.state = 'invoice'
                appr_transactions.tran_invoice_id = move_id.id

        return True



    #Kept for future use

    # def write(self,vals):
    #     if vals.get('insertion_type') == 'loi':
    #         vals.update({"root": self.env['res.users'].browse(SUPERUSER_ID).partner_id.id})
    #     return super(models.Model,self).write(vals)
