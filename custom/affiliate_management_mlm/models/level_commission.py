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


class LevelCommission(models.Model):
    _name = 'level.commission'
    _description = "Level Commission"

    level = fields.Integer(string="Level",required= True)
    aff_prg = fields.Many2one(string="Affiliate Program",comodel_name="affiliate.program")

    _sql_constraints = [
        ('level_unique', 'unique(level)',
         _('Previously defined level cannot be defined again!')),
        ('level_range','CHECK(level > 0)',
            _('Level value cannot be less than 1'))
    ]

    matrix_type = fields.Selection([("f","Fixed"),("p","Percentage")],required=True,default='f',string="Matrix Type")
    amount = fields.Float(string="Amount", required= True, default="0.0")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id, readonly='True')

    def write(self,vals):
        raise_exception = False
        for rec in self:
            if vals.get('amount') or vals.get('matrix_type'):
                if vals.get('matrix_type') == 'p' and vals.get('amount',0) > 100:
                    raise_exception = True
                elif vals.get('amount',0) > 100 and vals.get('matrix_type') != 'f' and rec.matrix_type == 'p':
                    raise_exception = True
                elif vals.get('matrix_type') == 'p' and not vals.get('amount', rec.amount) <= 100 and rec.amount > 100:
                    raise_exception = True
            if raise_exception:
                raise exceptions.UserError(_('Percentage amount cannot be greater than 100'))

        result = super(LevelCommission,self).write(vals)

    @api.model
    def create(self, data):
        if data.get('matrix_type') == 'p' and data.get('amount') > 100:
            raise exceptions.UserError(_('Percentage amount cannot be greater than 100'))

        return super(LevelCommission, self).create(data)
