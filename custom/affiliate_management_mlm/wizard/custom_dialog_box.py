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

from odoo import api, models, fields


class CustomDialogBox(models.TransientModel):
    _name = 'custom.dialog.box'
    _description = "Custom Dialog Box"

    msg = fields.Text(string="Message", readonly= True)

    def dialog_box(self, msg=False, title=False, **kw):
        if msg and title:
            record_id = self.set_msg(msg)

            return {
            'name': title,
            'view_mode': 'form',
            'view_id': self.env.ref('affiliate_management_mlm.view_custom_dialog_box').id,
            'res_model': 'custom.dialog.box',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': record_id.id
            }


    def set_msg(self, msg):
        return self.create({
        'msg': msg
        })
