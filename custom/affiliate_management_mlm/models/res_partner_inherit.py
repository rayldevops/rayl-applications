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

from odoo import api, fields, models, api, _
from odoo import SUPERUSER_ID
from odoo import exceptions
from odoo import http
from functools import wraps
import math

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'
    right_childs = 0
    left_childs = 0
    leaf_nodes = 0
    nodes = 0
    width = 0
    level = 1
    aff_ids = list()
    completed_levels = [0]
    free_child_nodes = list()
    apply_first_child_bonus = False

    def _get_domain_filter(self):
        return "[('is_affiliate','=',True),('bought_membership','=',True),'|',('left_child_aff','=',False),('right_child_aff','=',False)]"

    @api.depends('transaction_ids')
    def _check_amount_left(self):
        debit_amt = 0
        credit_amt = 0
        for transaction in self[0].transaction_ids:
            debit_amt += transaction.debit
            credit_amt += transaction.credit

        self[0].total_amount_left = credit_amt - debit_amt

    child_aff = fields.One2many(comodel_name="res.partner", inverse_name='parent_id', string="Child Affiliate")


    left_child_aff = fields.Many2one(string="Left Child Affiliate", comodel_name="res.partner", domain="[('is_affiliate','=',True),('parent_aff','=',False)]")
    right_child_aff = fields.Many2one(string="Right Child Affiliate", comodel_name="res.partner", domain="[('is_affiliate','=',True),('parent_aff','=',False)]")
    provide_level_commission = fields.Boolean(default=False)
    parent_aff = fields.Many2one(string="Parent Affiliate", comodel_name="res.partner")
    # parent_aff = fields.Many2one(string="Parent Affiliate", comodel_name="res.partner", domain=_get_domain_filter)

    mlm_order_id = fields.Many2one(string="Membership Order", comodel_name="sale.order", readonly="1")
    bought_membership = fields.Boolean(string="Bought Membership")
    upgrade_membership = fields.Boolean(string="Upgrade Membership")
    membership_state = fields.Selection(string="Membership Order State", selection=[('initial','Initial'),('draft','Draft'),('approve','Approved'),('cancel','Canceled')], default = 'initial')
    is_parent_set = fields.Boolean(string="Is Parent Set")
    aff_request_id = fields.Many2one(string="Affiliate Request Id", comodel_name="affiliate.request")
    is_dispute = fields.Boolean(string="Is in Dispute", readonly=False)
    dispute_remark = fields.Text(string="Remark", readonly=True)

    total_amount_left = fields.Float(String="Total Left Amount", compute=_check_amount_left)

    # ------------------MLM configuration----Bonus---Start-------->
    is_first_child_bonus_applied = fields.Boolean(string="Is First Child Bonus Applied")
    bonus_level = fields.Integer(string="Reached Bonus Level", readonly= True)
    transaction_ids = fields.One2many(string="Transaction Ids", comodel_name='mlm.transaction', inverse_name='partner_id')
    # ------------------MLM configuration----Bonus---End-------->

    def name_get(self):
        if self.env.context.get('name_get_override', False):
            res = []
            for record in self:
                res.append((record.id, record.name+" [ "+record.res_affiliate_key+" ]"))
            return res

        return super(ResPartnerInherit,self).name_get()

    @api.model
    def affi_key_check(self,affi_key):

        ids = self.env['res.partner'].sudo().search([("is_affiliate","=","True")])

        affi_keys = [id.res_affiliate_key for id in ids]

        for id in ids:
            if affi_key == id.res_affiliate_key:
                return id
        return False

    def set_root(self):

        if not self.is_affiliate:
            raise exceptions.ValidationError(_("Partner is required to be an affiliate, in order to set the root."))
        elif not self.bought_membership:
            raise exceptions.ValidationError(_("Cannot set root, as Membership is missing."))

        mlm_config = self.env['affiliate.program'].get_mlm_configuration()
        root = mlm_config.get('root')

        if self == self.env.ref('base.partner_admin'):
            raise exceptions.ValidationError(
            _("Error while validating constraint\nError ! Cannot assign parent affiliate for Admin ."))

        parent_with_free_childs = root.mlm_tree(root).get('free_child_nodes')

        self.parent_aff = parent_with_free_childs[0].id
        self.provide_level_commission = True

        position = "<strong><em>Left Child Affiliate</em></strong>" if self.parent_aff.left_child_aff == self else "<strong><em>Right Child Affiliate</em></strong>"
        msg = "Root is assigned <em>Automatically</em>.<br><strong>"+ self.name+ "</strong>" + " is now the " + position + " of " + "<strong>" +self.parent_aff.name +"</strong>."
        response = self.env['custom.dialog.box'].dialog_box(msg=msg, title="Approved")

        return response

    #Kept for future use

    # def set_root(self):
    #     mlm_config = self.env['affiliate.program'].get_mlm_configuration()
    #     if mlm_config['root'].left_child_aff and mlm_config['root'].right_child_aff:
    #         raise exceptions.UserError(_("Both the childs of root are occupied, please set another parent affiliate."))
    #
    #
    #     self.parent_aff = mlm_config['root']

    def remove_relation(self, parent_aff):

        if parent_aff.left_child_aff == self:
            parent_aff.left_child_aff = ""
            return 'left'
        elif parent_aff.right_child_aff == self:
            # parent_aff.right_child_aff = ""
            pass
            return 'right'

    def check_parent_childs(self,root):

        if root.left_child_aff != self and root.right_child_aff != self:
            if not root.left_child_aff:
                return True

            if not root.right_child_aff:
                return True

        return False


    #Kept for future use

    # def check_parent_in_child(self, left_child, right_child, parent_id):
    #     if (left_child and left_child.id == parent_id) or (right_child and right_child.id == parent_id):
    #         raise exceptions.ValidationError(
    #         _("""Error while validating constraint
    #         Error ! You cannot assign child as parent affiliate.
    #         """))
    #     if left_child:
    #         self.check_parent_in_child(left_child.left_child_aff, left_child.right_child_aff, parent_id)
    #     if right_child:
    #         self.check_parent_in_child(right_child.left_child_aff, right_child.right_child_aff, parent_id)

    def check_recursion_contraints(self, parent_aff_id):
        if self.id == parent_aff_id:
            raise exceptions.ValidationError(
            _("""Error while validating constraint
            Error ! You cannot assign """+self.name+""" as its own parent affiliate.
            """))
        elif self.left_child_aff.id == parent_aff_id or self.right_child_aff.id == parent_aff_id:
            raise exceptions.ValidationError(
            _("""Error while validating constraint
            Error ! You cannot assign child as parent affiliate.
            """))

        #Kept for future use

        # self.check_parent_in_child(self.left_child_aff, self.right_child_aff, parent_aff_id)

        return True

    def insert(self,root):

        if root.left_child_aff != self and root.right_child_aff != self:
            if not root.left_child_aff:
                root.left_child_aff = self
                return 'left'

            if not root.right_child_aff:
                # root.right_child_aff = self
                pass
                return 'right'

        #Add the automatic insertion algo in future if required

        return False

    def set_parent_affiliate(self, parent_aff_id):
        if self.is_affiliate and self.parent_aff:
            self.remove_relation(self.parent_aff)

        if self.is_affiliate:
            self.insert(parent_aff_id)

        self.is_parent_set = True
        if self.aff_request_id:
            self.aff_request_id.parent_aff_key = parent_aff_id.res_affiliate_key
        else:
            aff_request_id = self.env['affiliate.request'].sudo().search([('partner_id','=',self.id)],limit=1)
            self.aff_request_id = aff_request_id.id
            aff_request_id.parent_aff_key = parent_aff_id.res_affiliate_key

        self.is_dispute = False
        self.dispute_remark = ""


    def write(self,vals):

        #Sets the parent affiliate for a partner and also sets partner as left or right child of its parent affiliate
        if vals.get('parent_aff') and (self.is_affiliate or self.aff_request_id):

            self.check_recursion_contraints(vals.get('parent_aff'))

            parent_aff_id = self.browse(vals.get('parent_aff'))

            self.set_parent_affiliate(parent_aff_id)

            # if not self.check_parent_childs(parent_aff_id):
            #     raise exceptions.ValidationError(_("Both the childs of parent affiliate are occupied. Please change the parent affiliate."))

            # self.set_parent_affiliate(parent_aff_id)

            # if self.is_affiliate and self.parent_aff:
            #
            #     self.remove_relation(self.parent_aff)
            #
            # if self.is_affiliate:
            #
            #     self.insert(parent_aff_id)
            #
            # self.is_parent_set = True
            # if self.aff_request_id:
            #     self.aff_request_id.parent_aff_key = parent_aff_id.res_affiliate_key
            # else:
            #     aff_request_id = self.env['affiliate.request'].sudo().search([('partner_id','=',self.id)],limit=1)
            #     self.aff_request_id = aff_request_id.id
            #     aff_request_id.parent_aff_key = parent_aff_id.res_affiliate_key
            #
            # self.is_dispute = False
            # self.dispute_remark = ""

        # aff_obj = self.env['affiliate.request'].sudo().search([('partner_id', '=', self.id)])
        # parent_aff = self.env['res.partner'].sudo().search([('res_affiliate_key', '=', aff_obj.website_parent_affiliate_key)], limit=1)
        # if aff_obj:
            # for record in self:
            # if parent_aff:
            #     parent_aff.child_aff = [(4, parent_aff.id)]
            # vals['child_aff'] = [(4, parent_aff.id)]
                # self.child_aff = (4, parent_aff.id)

        #Removes the parent affiliate for a partner and also removes partner as left or right child of its parent affiliate
        if vals.get('parent_aff') == False and (self.is_affiliate or self.aff_request_id):

            self.is_parent_set = False
            if self.aff_request_id:
                self.aff_request_id.parent_aff_key = ""
            else:
                aff_request_id = self.env['affiliate.request'].sudo().search([('partner_id','=',self.id)],limit=1)
                aff_request_id.parent_aff_key = ""

            self.is_dispute = True
            self.dispute_remark = _("Parent Affiliate is missing.")

            if self.is_affiliate and self.parent_aff:
                self.remove_relation(self.parent_aff)

        #Kept for future use

        # left_aff_id = None
        # right_aff_id = None
        #
        # if vals.get('left_child_aff') == False or vals.get('right_aff_id') == False:
        #     left_aff_id = self.left_child_aff
        #     right_aff_id = self.right_child_aff
        #

        result = super(models.Model,self).write(vals)

        #Kept for future use

        # if vals.get('left_child_aff') == False and self.aff_request_id:
        #     left_aff_id.parent_aff = False
        #
        # if vals.get('right_child_aff') == False and self.aff_request_id:
        #     right_aff_id.parent_aff = False
        #
        # if vals.get('left_child_aff') and self.aff_request_id:
        #     if not self.left_child_aff.parent_aff:
        #         self.left_child_aff.parent_aff = self
        #
        # if vals.get('right_child_aff') and self.aff_request_id:
        #     if not self.right_child_aff.parent_aff:
        #         self.right_child_aff.parent_aff = self

        return result

#--------------------------MLM Tree-------Start------->

    # def wrapper(self,**kw):
    #     inst = ResPartnerInherit
    #     inst.right_childs = 0
    #     inst.left_childs = 0
    #     inst.leaf_nodes = 0
    #     inst.nodes = 0
    #     inst.width = 0
    #     inst.level = 1
    #     inst.aff_ids = list()
    #     inst.completed_levels = [0]
    #     inst.free_child_nodes = list()
    #     inst.apply_first_child_bonus = False

    def left_child_count(self, parent):
        ResPartnerInherit.left_childs += 1
        ResPartnerInherit.nodes += 1

        if ResPartnerInherit.left_childs == 1 and not parent.is_first_child_bonus_applied:
            ResPartnerInherit.apply_first_child_bonus = True


    def right_child_count(self, parent):
        ResPartnerInherit.right_childs += 1
        ResPartnerInherit.nodes += 1

        if ResPartnerInherit.nodes == math.pow(2 , ResPartnerInherit.level):
            ResPartnerInherit.nodes = 0
            ResPartnerInherit.completed_levels.append(ResPartnerInherit.level)
            ResPartnerInherit.level += 1

    def leaf_node_count(self):
        ResPartnerInherit.leaf_nodes += 1

    def child_count(self, child_id, child_pos, parent):

        ResPartnerInherit.aff_ids.append(child_id)

        if child_pos == 'left':
            self.left_child_count(parent)
        else:
            self.right_child_count(parent)

    def _root_child(self, child, parent):

        self.child_count(child[0], child[1], parent)

        child_childs = list()

        if child[0].left_child_aff:
            child_childs.append((child[0].left_child_aff,'left'))
        else:
            if child[0] not in ResPartnerInherit.free_child_nodes:
                ResPartnerInherit.free_child_nodes.append(child[0])

        if child[0].right_child_aff:
            # child_childs.append((child[0].right_child_aff,'right'))
            pass
        else:
            if child[0] not in ResPartnerInherit.free_child_nodes:
                ResPartnerInherit.free_child_nodes.append(child[0])
            ResPartnerInherit.width += 1
        if not child[0].left_child_aff and not child[0].right_child_aff:
            self.leaf_node_count()

        return child_childs

    def _root_childs(self, left_child, right_child, root):

        # Bredth First Search(BFS)
        childs = list()

        if left_child:
            childs.append((left_child,'left'))
        else:
            if root not in ResPartnerInherit.free_child_nodes:
                ResPartnerInherit.free_child_nodes.append(root)
        if right_child:
            childs.append((right_child,'right'))
        else:
            if root not in ResPartnerInherit.free_child_nodes:
                ResPartnerInherit.free_child_nodes.append(root)

        while childs:
            child_childs = self._root_child(childs[0], root)
            childs.pop(0)
            childs = childs + child_childs

    # @initialize_default
    @api.model
    def mlm_tree(self,root, **kw):
        # self.wrapper()
        self._root_childs(root.left_child_aff, root.right_child_aff, root)
        Rpi = ResPartnerInherit
        return {
        'leaf_nodes': Rpi.leaf_nodes,
        'width': Rpi.width,
        'childs': Rpi.left_childs + Rpi.right_childs,
        'left_childs': Rpi.left_childs,
        'right_childs': Rpi.right_childs,
        'completed_levels': Rpi.completed_levels,
        'apply_first_child_bonus': Rpi.apply_first_child_bonus,
        'aff_ids': Rpi.aff_ids,
        'free_child_nodes': Rpi.free_child_nodes,
        }

#--------------------------MLM Tree-------End------->
