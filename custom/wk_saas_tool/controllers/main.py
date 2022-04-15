# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
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
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from werkzeug.exceptions import BadRequest
from odoo.http import request
from odoo import http
from odoo.addons.web.controllers.main import Home, ensure_db
import logging
import base64

_logger = logging.getLogger(__name__)


def setup_db(self, httprequest):
    db = httprequest.session.db
    # Check if session.db is legit
    if db:
        if db not in http.db_filter([db], httprequest=httprequest):
            _logger.warn("Logged into database '%s', but dbfilter "
            "rejects it; logging session out.", db)
            httprequest.session.logout()
            db = None
    if not db:
        if  httprequest.args.get('db') and httprequest.args.get('login') and httprequest.args.get('passwd'):
            httprequest.session.db = httprequest.args.get('db')
        else:
            httprequest.session.db = http.db_monodb(httprequest)
http.Root.setup_db = setup_db


class SaaSLogin(Home):

    @http.route('/saas/login', type='http', auth='public', website=True, sitemap=False)
    # @http.route('/saas/login', type='http', auth='none', sitemap=False)
    def autologin(self, **kw):
        """login user via Odoo Account provider
        QUERY : SELECT COALESCE(password, '') FROM res_users WHERE id=1;
        import base64
        base64.b64encode(s.encode('utf-8'))
        """
        _logger.info("---   --- --123 - -- - -")
        db = request.params.get('db') and request.params.get('db').strip()
        dbname = kw.pop('db', None)
        redirect_url = kw.pop('redirect_url', '/web')
        login = kw.pop('login', 'admin')
        password = kw.pop('passwd', None)
        if not dbname:
            return BadRequest()
        uid = request.session.authenticate(dbname, login, password)
        request.params['login_success'] = True

        return http.redirect_with_hash(redirect_url)
