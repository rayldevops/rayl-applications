# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, http, _

from odoo.http import request
import urllib
import re
import json


class MediaSocialList(models.Model):

    _name = "share.social.list"
    _description = "List media social in use"
    _rec_name = 'name'
    _order = 'sequence, name'

    name = fields.Char(string='Social Media', readonly=True)
    code = fields.Char(string='Code social Media', readonly=True)
    sequence = fields.Integer(string='Sequence', default=10)
    domain_media = fields.Char(string='Domain', readonly=True)
    image_svg = fields.Html(readonly=True)
    parameter_url = fields.Char(readonly=True)

    def format_string(self, name):
        name_format = name
        list = [" ", ".", "_"]
        for i in list:
            name_format = name_format.replace(i, "")

        return name_format

    @api.model
    def social_list(self):
        media = []
        record_set = self.sudo().search([])
        for media_list in record_set:
            media.append(self.format_string(name=media_list.name))

        return media

    @api.model
    def parameter_social_url(self, url, title, social, image):

        social = social.lower()
        path_url = urllib.parse.quote(url.encode('utf8'))
        title = urllib.parse.quote(title.encode('utf8'))
        image = urllib.parse.quote(image.encode('utf8'))
        social_media = self.sudo().search([("code", "=", social)])
        media_social_url = ''

        for media in social_media:
            if media.code in ['pinterest']:
                media_social_url = u'{}{}'.format(media.domain_media, media.parameter_url)
                media_social_url = media_social_url.format(postUrl=path_url, postTitle=title, postImage=image)
            else:
                media_social_url = u'{}{}'.format(media.domain_media, media.parameter_url)
                media_social_url = media_social_url.format(postUrl=path_url, postTitle=title)

        return media_social_url.replace("%5C", "")

    @api.model
    def web_search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """
        Performs a search_read and a search_count.

        :param domain: search domain
        :param fields: list of fields to read
        :param limit: maximum number of records to read
        :param offset: number of records to skip
        :param order: columns to sort results
        :return: {
            'records': array of read records (result of a call to 'search_read')
            'length': number of records matching the domain (result of a call to 'search_count')
        }
        """
        records = self.search_read(domain, fields, offset=offset, limit=limit, order=order)
        if not records:
            return {
                'length': 0,
                'records': []
                }
        if limit and (len(records) == limit or self.env.context.get('force_search_count')):
            length = self.search_count(domain)
        else:
            length = len(records) + offset
        return {
            'length': length,
            'records': records
            }