# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import json
import logging
import werkzeug
import math
from odoo import http, tools, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_profile.controllers.main import WebsiteProfile
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import AccessError, UserError
from odoo.http import request
from odoo.osv import expression
import time
from odoo.http import request
from authlib.jose import jwt
import os
import logging

_logger = logging.getLogger(__name__)


class JistiMeet(http.Controller):

    exp_time = 7200  # 7200 Seconds = 2 Hours
    nbf_seconds = 10  # Seconds

    @http.route('/meet/<int:id>/', type='http', auth="public", website=True)
    def jitsi_meet(self, id, **kwargs):
        record = request.env['jitsi.meet'].sudo().browse(id)
        if record:
            if not record.closed:
                data = {
                    'data': record,
                }
                return request.render("se_jitsi_meet.meet", data)
            else:
                return request.render("se_jitsi_meet.meet_closed")
        else:
            return request.render("se_jitsi_meet.meet_closed")

    @http.route('/get-jwt-token', type='http', auth="public", website=True,  methods=['GET'])
    def generate_jwt_token(self):
        app_id = request.env['ir.config_parameter'].sudo().get_param('jitsi.app_id')
        header = {"kid": request.env['ir.config_parameter'].sudo().get_param('jitsi.kid'),
                  "typ": "JWT", "alg": "RS256"}
        _time = time.time()
        payload = {"aud": "jitsi", "iss": "chat",
                   "iat": int(_time),
                   "exp": int(_time + JistiMeet.exp_time),
                   "nbf": int(_time - JistiMeet.nbf_seconds),
                   "context": {
                                "features": {
                                  "livestreaming": True,
                                  "outbound-call": True,
                                  "sip-outbound-call": False,
                                  "transcription": True,
                                  "recording": True
                                },
                                "user": {
                                  "moderator": True,
                                  # "name": "raylgeneral2022@gm12ail.com",
                                  # "id": "auth|625943122a651ac100704bb273",
                                  # "avatar": "",
                                  # "email": "raylgeneral201222@gmail.com"
                                }
                              },
                   "room": "*",
                   "sub": app_id
                   }
        script_dir = os.path.dirname(__file__)
        fp = os.path.join(script_dir, 'jitsi_private_key.pk')
        with open(fp, "rb") as pem_file:
            private_key = pem_file.read()
        return jwt.encode(header, payload, private_key)


class JitsiWebhook(http.Controller):

    @http.route('/jitsi_recording', type='json', auth="public", website=True,  methods=['POST'])
    def generate_jwt_token(self, **kwargs):
        _logger.info("Recording Uploaded Webhook Response Received Successfully")
        data = request.jsonrequest
        download_link = data.get('data').get('preAuthenticatedLink')
        mail_server_id = request.env['ir.mail_server'].search([], limit=1)
        # _logger.info(f" Json Request Parameters {data}")
        # _logger.info(f" Download Link {download_link}")
        body = _(
            '<div>'
            ' <p>Please click on the below link for downloading the meeting recording</p>'
            '%s'
            '</div>' % download_link)
        main_content = {
            'subject': "RAYL Meet Download Link",
            # 'author_id': request.env.user.partner_id.email,
            'mail_server_id': mail_server_id.id,
            'email_from': "noreply@rayl.app",
            'body_html': body,
            'email_to': request.env.user.partner_id.email,
        }
        request.env['mail.mail'].sudo().create(main_content).sudo().send()
        return {"data": "Success"}
