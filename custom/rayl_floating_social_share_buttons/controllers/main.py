# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import werkzeug
import itertools
import pytz
import babel.dates
from collections import OrderedDict

from odoo import http, fields
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.controllers.main import QueryURL
from odoo.api import call_kw, Environment
from odoo.models import check_method_name
from odoo.http import request
from odoo.osv import expression
from odoo.tools import html2plaintext
from odoo.tools.misc import get_lang


class WebsiteShareFloating(http.Controller):

    def _call_kw(self, model, method, args, kwargs):
        check_method_name(method)
        return call_kw(request.env[model], method, args, kwargs)

    @http.route('/web/dataset/call_share_floating', type='json', auth="public", website=True)
    def call(self, model, method, args, domain_id=None, context_id=None):
        return self._call_kw(model, method, args, {})

    @http.route('/web/dataset/search_read_share', type='json', auth="public", website=True)
    def search_read(self, model, fields=False, offset=0, limit=False, domain=None, sort=None):
        return self.do_search_read(model, fields, offset, limit, domain, sort)

    def do_search_read(self, model, fields=False, offset=0, limit=False, domain=None, sort=None):
        """ Performs a search() followed by a read() (if needed) using the
        provided search criteria

        :param str model: the name of the model to search on
        :param fields: a list of the fields to return in the result records
        :type fields: [str]
        :param int offset: from which index should the results start being returned
        :param int limit: the maximum number of records to return
        :param list domain: the search domain for the query
        :param list sort: sorting directives
        :returns: A structure (dict) with two keys: ids (all the ids matching
                  the (domain, context) pair) and records (paginated records
                  matching fields selection set)
        :rtype: list
        """
        Model = request.env[model]
        return Model.web_search_read(domain, fields, offset=offset, limit=limit, order=sort)
