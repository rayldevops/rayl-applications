from odoo import fields, http
from odoo.http import request
import odoo
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.web.controllers.main import Home
from odoo.addons.auth_signup.controllers.main import Home
from odoo.addons.auth_signup.models.res_users import SignupError

import babel.messages.pofile
import base64
import copy
import datetime
import functools
import glob
import hashlib
import io
import itertools
import jinja2
import json
import logging
import operator
import os
import re
import sys
import tempfile

import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from collections import OrderedDict, defaultdict, Counter
from werkzeug.urls import url_encode, url_decode, iri_to_uri
from lxml import etree
import unicodedata


import odoo
import odoo.modules.registry
from odoo.api import call_kw, Environment
from odoo.modules import get_module_path, get_resource_path
from odoo.tools import image_process, topological_sort, html_escape, pycompat, ustr, apply_inheritance_specs, lazy_property
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools.translate import _
from odoo.tools.misc import str2bool, xlsxwriter, file_open
from odoo.tools.safe_eval import safe_eval, time
from odoo import http, tools
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception, Response
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.models import check_method_name
from odoo.service import db, security

_logger = logging.getLogger(__name__)

# db_list = http.db_list
#
# db_monodb = http.db_monodb
#
# def abort_and_redirect(url):
#     r = request.httprequest
#     response = werkzeug.utils.redirect(url, 302)
#     response = r.app.get_response(r, response, explicit_session=False)
#     werkzeug.exceptions.abort(response)
#
#
# def ensure_db(redirect='/web/database/selector'):
#     # This helper should be used in web client auth="none" routes
#     # if those routes needs a db to work with.
#     # If the heuristics does not find any database, then the users will be
#     # redirected to db selector or any url specified by `redirect` argument.
#     # If the db is taken out of a query parameter, it will be checked against
#     # `http.db_filter()` in order to ensure it's legit and thus avoid db
#     # forgering that could lead to xss attacks.
#     db = request.params.get('db') and request.params.get('db').strip()
#
#     # Ensure db is legit
#     if db and db not in http.db_filter([db]):
#         db = None
#
#     if db and not request.session.db:
#         # User asked a specific database on a new session.
#         # That mean the nodb router has been used to find the route
#         # Depending on installed module in the database, the rendering of the page
#         # may depend on data injected by the database route dispatcher.
#         # Thus, we redirect the user to the same page but with the session cookie set.
#         # This will force using the database route dispatcher...
#         r = request.httprequest
#         url_redirect = werkzeug.urls.url_parse(r.base_url)
#         if r.query_string:
#             # in P3, request.query_string is bytes, the rest is text, can't mix them
#             query_string = iri_to_uri(r.query_string)
#             url_redirect = url_redirect.replace(query=query_string)
#         request.session.db = db
#         abort_and_redirect(url_redirect)
#
#     # if db not provided, use the session one
#     if not db and request.session.db and http.db_filter([request.session.db]):
#         db = request.session.db
#
#     # if no database provided and no database in session, use monodb
#     if not db:
#         db = db_monodb(request.httprequest)
#
#     # if no db can be found til here, send to the database selector
#     # the database selector will redirect to database manager if needed
#     if not db:
#         werkzeug.exceptions.abort(werkzeug.utils.redirect(redirect, 303))
#
#     # always switch the session to the computed db
#     if db != request.session.db:
#         request.session.logout()
#         abort_and_redirect(request.httprequest.url)
#
#     request.session.db = db


class AuthSignupHome(Home):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()
        cust = request.env['ir.config_parameter'].sudo().search(
            [('key', '=', 'website_terms_conditions.is_terms_and_conditions')])
        # cust=request.env["res.config.settings"].sudo().search([("is_terms_and_conditions", "=", True)])
        if cust:
            cust.value = True
            qcontext['enable1'] = True
        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                if qcontext.get('token'):
                    User = request.env['res.users']
                    user_sudo = User.sudo().search(
                        User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                    )
                    template = request.env.ref('auth_signup.mail_template_user_signup_account_created',
                                               raise_if_not_found=False)
                    if user_sudo and template:
                        template.sudo().send_mail(user_sudo.id, force_send=True)
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

# class HomeInherit(Home):

    # @http.route('/web/login', type='http', auth="none")
    # def web_login(self, redirect=None, **kw):
    #     # ensure_db()
    #     request.params['login_success'] = False
    #     if request.httprequest.method == 'GET' and redirect and request.session.uid:
    #         return http.redirect_with_hash(redirect)
    #
    #     if not request.uid:
    #         request.uid = odoo.SUPERUSER_ID
    #
    #     values = request.params.copy()
    #     try:
    #         values['databases'] = http.db_list()
    #     except odoo.exceptions.AccessDenied:
    #         values['databases'] = None
    #
    #     if request.httprequest.method == 'POST':
    #         old_uid = request.uid
    #         try:
    #             uid = request.session.authenticate(request.session.db, request.params['login'],
    #                                                request.params['password'])
    #             request.params['login_success'] = True
    #             return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
    #         except odoo.exceptions.AccessDenied as e:
    #             request.uid = old_uid
    #             if e.args == odoo.exceptions.AccessDenied().args:
    #                 values['error'] = ("Wrong login/password")
    #             else:
    #                 values['error'] = e.args[0]
    #     else:
    #         if 'error' in request.params and request.params.get('error') == 'access':
    #             values['error'] = ('Only employees can access this database. Please contact the administrator.')
    #
    #     if 'login' not in values and request.session.get('auth_login'):
    #         values['login'] = request.session.get('auth_login')
    #
    #     if not odoo.tools.config['list_db']:
    #         values['disable_database_manager'] = True
    #
    #     response = request.render(''
    #                               'web.login', values)
    #     response.headers['X-Frame-Options'] = 'DENY'
    #     return response


class WebsiteSaleInherit(WebsiteSale):
#
#     @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
#     def payment(self, **post):
#         """ Payment step. This page proposes several payment means based on available
#         payment.acquirer. State at this point :
#
#          - a draft sales order with lines; otherwise, clean context / session and
#            back to the shop
#          - no transaction in context / session, or only a draft one, if the customer
#            did go to a payment.acquirer website but closed the tab without
#            paying / canceling
#         """
#         order = request.website.sale_get_order()
#         redirection = self.checkout_redirection(order)
#         if redirection:
#             return redirection
#
#         render_values = self._get_shop_payment_values(order, **post)
#         render_values['only_services'] = order and order.only_services or False
#
#         if render_values['errors']:
#             render_values.pop('acquirers', '')
#             render_values.pop('tokens', '')
#
#         return request.render("website_sale.payment", render_values)

    @http.route(['/conditions'], type='http', auth="public", website=True, sitemap=False)
    def terms_condition(self, **post):
        config = request.env['ir.config_parameter'].sudo().search([('key','=','website_terms_conditions.terms_and_conditions')])
        a = config.value

        return request.render("website_terms_conditions.terms_condition", {'setting': a})

    @http.route(['/report/pdf/terms_receipt_download'], type='http', auth='public', methods=['POST'])
    def download_receipts(self,**post):
        config = request.env['ir.config_parameter'].sudo().search([('key','=','website_terms_conditions.terms_and_conditions')])
        pdf, _ = request.env.ref('website_terms_conditions.action_print_terms').sudo()._render_qweb_pdf([int(config.id)])
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf)),
                          ('Content-Disposition', 'COA; filename="Terms and Conditions.pdf"')]
        return request.make_response(pdf, headers=pdfhttpheaders)