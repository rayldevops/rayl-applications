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


class MLMTransaction(models.Model):
    _name = 'mlm.transaction'
    _description = "RAP Transaction Model"


    name = fields.Char(string='Name', readonly = True)
    partner_id = fields.Many2one(string="Affiliate", comodel_name="res.partner", domain="[('is_affiliate','=',True)]", required= True)
    credit = fields.Float(string="Credit")
    debit = fields.Float(string="Debit")
    summary = fields.Char(string="Transaction Summary")
    active = fields.Boolean('Active', default=True, help="If unchecked, it will allow you to hide the RAP transaction without removing it.")

    state = fields.Selection(string="Transaction State", selection=[('pending','Pending'),('approve','Approved'),('cancel','Canceled'),('invoice','Invoiced'),('paid','Paid')], default='pending')
    bonus_type = fields.Selection(string="Bonus Type",  selection=[('fcb','First Child Bonus'),('lcb','Level Completion Bonus'),('level_commission','Level Commission')], required= True)

    tran_invoice_id = fields.Many2one(string="Invoice Id", comodel_name="account.move")



    def transaction_approve(self):
        self.state = 'approve'

    def transaction_cancel(self):
        self.state = 'cancel'

    def mlm_bonus_transactions(self):

        mlm_config = self.env['affiliate.program'].get_mlm_configuration()
        root = mlm_config.get('root')

        root_mlm_tree_data = root.mlm_tree(root)
        aff_ids = list(filter(lambda aff_id: aff_id.bought_membership == True, root_mlm_tree_data.get('aff_ids')))
        self.add_bonus_transaction(root, root_mlm_tree_data, mlm_config)

        for aff_id in aff_ids:
            mlm_tree_data = aff_id.mlm_tree(aff_id)
            self.add_bonus_transaction(aff_id, mlm_tree_data, mlm_config)

    @api.model
    def create(self, vals):

        vals['name'] = self.env['ir.sequence'].next_by_code('mlm.transaction')
        new_tran =  super(MLMTransaction,self).create(vals)
        return new_tran

    def _get_amt(self, amt, matrix_type, product):
        if matrix_type == 'p':
            amt = product.lst_price * amt/100
        return amt

    @api.model
    def add_bonus_transaction(self, partner_id, mlm_tree_data, mlm_config = {}):

        vals={}

        if not mlm_config:
            mlm_config = self.env['affiliate.program'].get_mlm_configuration()

        if partner_id.provide_level_commission:
            parent_id = partner_id.parent_aff
            # for level_commission in mlm_config.get('level_commission_ids',[]):
            #     if parent_id and level_commission:
            #         vals.update({
            #         'credit': self._get_amt(level_commission.amount, level_commission.matrix_type, mlm_config.get('mlm_membership_product')),
            #         'summary': "Level %s Commission for the joining of %s[ %s ]"%(level_commission.level, partner_id.name, partner_id.res_affiliate_key),
            #         'bonus_type': "level_commission",
            #         'name': parent_id.name,
            #         'partner_id':parent_id.id
            #         })
            #
            #         self.create(vals)
            #         parent_id = parent_id.parent_aff
            #     else:
            #         break
            level_commissions = mlm_config.get('level_commission_ids',False)
            max_commission_level = level_commissions and max(level_commissions) or 0
            parent_level = 1
            while parent_id and parent_level <= max_commission_level:
                if parent_level in level_commissions:
                    vals.update({
                            'credit': self._get_amt(level_commissions[parent_level].amount, level_commissions[parent_level].matrix_type, mlm_config.get('mlm_membership_product')),
                            'summary': "Level %s Commission for the joining of %s[ %s ]"%(parent_level, partner_id.name, partner_id.res_affiliate_key),
                            'bonus_type': "level_commission",
                            'name': parent_id.name,
                            'partner_id':parent_id.id
                            })
                    self.create(vals)
                parent_id = parent_id.parent_aff
                parent_level += 1

            partner_id.provide_level_commission = False

        if mlm_config.get('allow_fcb_bonus'):
            if mlm_tree_data.get('apply_first_child_bonus') and not partner_id.is_first_child_bonus_applied and not 'fcb' in [t.bonus_type for t in partner_id.transaction_ids]:
                partner_id.is_first_child_bonus_applied = True
                vals.update({
                'name': partner_id.name,
                'partner_id':partner_id.id,
                'credit': self._get_amt(mlm_config.get('first_child_bonus_amount'), mlm_config.get('fcb_matrix_type'), mlm_config.get('mlm_membership_product')),
                'summary': "First Child Bonus for the joining of %s[ %s ]"%(partner_id.left_child_aff.name, partner_id.left_child_aff.res_affiliate_key),
                'bonus_type': "fcb",
                })

                self.create(vals)

        if mlm_config.get('allow_lcb_bonus'):
            if mlm_tree_data.get('completed_levels') and partner_id.bonus_level < mlm_tree_data.get('completed_levels')[-1]:

                completed_levels = mlm_tree_data.get('completed_levels')[mlm_tree_data.get('completed_levels').index(partner_id.bonus_level) + 1 :]
                amt = self._get_amt(mlm_config.get('level_bonus_amount'), mlm_config.get('lcb_matrix_type'), mlm_config.get('mlm_membership_product'))
                for completed_level in completed_levels:

                    partner_id.bonus_level = completed_level
                    vals.update({
                    'name': partner_id.name,
                    'partner_id':partner_id.id,
                    'credit': amt,
                    'summary': "Level " +str(completed_level)+"Completion Bonus." ,
                    'bonus_type': "lcb",
                    })

                    self.create(vals)
