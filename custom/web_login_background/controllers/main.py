
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.website_terms_conditions.controllers.main import AuthSignupHomeIn
from odoo.addons.web.controllers.main import Home

import pytz
import datetime
import logging

from odoo import http
from odoo.http import request
_logger = logging.getLogger(__name__)


def set_background():
    request.params['background_src'] = 'background-image: url(/web_login_background/static/src/img/apptive_login.png);background-position: center;background-attachment: fixed;background-size: cover;background-repeat: no-repeat'
    request.params['nav_color'] = 'background-color: rgba(0, 0, 0, 0.15) !important;color:#fff !important;'
    request.params['footer_color'] = 'background-color: rgba(0, 0, 0, 0.15) !important;color:#fff !important;'

#----------------------------------------------------------
# Odoo Web web Controllers
#----------------------------------------------------------


class LoginHome(Home):

    @http.route('/web/login', type='http', auth="public")
    def web_login(self, redirect=None, **kw):
        set_background()
        return super(LoginHome, self).web_login(redirect, **kw)

class AuthResetPasswordHomeInherit(AuthSignupHome):

    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        set_background()
        return super(AuthResetPasswordHomeInherit, self).web_auth_reset_password(*args, **kw)


class AuthSignupHomeInherit(AuthSignupHomeIn):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        set_background()
        return super(AuthSignupHomeInherit, self).web_auth_signup(*args, **kw)
