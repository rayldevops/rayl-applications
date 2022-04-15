# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.web_editor.controllers.main import Web_Editor


class Web_Editor(Web_Editor):

    @http.route(["/website_sale/field/website_description"], type='http', auth="user")
    def website_description_FieldTextHtml(self, model=None, res_id=None, field=None, callback=None, **kwargs):
        kwargs['snippets'] = '/website/snippets'
        kwargs['template'] = 'gtica_shop_description_product.FieldTextHtml'
        return self.FieldTextHtml(model, res_id, field, callback, **kwargs)


