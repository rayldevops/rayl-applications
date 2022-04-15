import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from odoo import models, fields,api,_
import random, string
import datetime
from . pg_query import PgQuery

class SaaSResPartnerInherit(models.Model):

    _inherit = 'res.partner'
    _description = "SaaS ResPartner Inherit Model"


    is_saas_user = fields.Boolean('SaaS User Created', default=False)
    is_saas_contract = fields.Boolean('SaaS Contract Created', default=False)
    is_saas_client = fields.Boolean('SaaS Client Created', default=False)
    saas_user_id = fields.Char('SaaS User ID')
    saas_contract_id = fields.Char('SaaS Contract ID')
    saas_url = fields.Char('SaaS URL')
    saas_domain_name = fields.Char('SaaS Domain Name')
    password = fields.Char('SaaS Domain Pass')
    client_url = fields.Char('SaaS Domain Client Url')
    login = fields.Char('SaaS Domain Login')

    def action_create_instance(self):
        if self.saas_domain_name:
            saas_user = self.env['saas.user'].sudo()
            saas_user.saas_createuser(self.id, self.saas_domain_name)
        else:
            raise UserError(_("SaaS Domain name is not setup"))

    def login_to_client_instance(self):
        for obj in self:
            query = "SELECT login, COALESCE(password, '') FROM res_users WHERE id=6;"
            host='10.114.0.5'
            database='girishtest.rayl.website'
            user='odoosaas'
            password='saasodoo'
            port='5432'
            pgX = PgQuery(host, database, user, password, port)

            with pgX:
                response = pgX.selectQuery(query)
            if response:
                login = response[0][0]
                password = response[0][1]
                res_partner = self.env['res.partner'].sudo().search([('id', '=', 20)])
                res_partner.write({'client_url': 'https://'+res_partner.saas_url,
                                   'login': login,
                                   'password': password})
                # login_url = "{}/saas/login?db={}&login={}&passwd={}".format(obj.client_url, obj.database_name, login, password)
                # return {
                #     'type': 'ir.actions.act_url',
                #     'url': login_url,
                #     'target': 'new',
                # }
            else:
                raise UserError("Unknown Error!")