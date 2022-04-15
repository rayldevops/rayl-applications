from odoo import _, api, fields, models
import xmlrpc
import logging
import xmlrpc.client
from datetime import date
from odoo.exceptions import UserError
import requests
import json
import re

_logger = logging.getLogger(__name__)


class SaasUser(models.Model):
    _name = 'saas.user'

    def synch_rayl_community_user(self, partner, domain_name):
        _logger.info("Started to sync rayl community user")
        rayl_community_url = 'https://app.rayl.community/api/v1/user/get-by-email'
        rayl_community_update_url = 'https://app.rayl.community/api/v1/user'
        rayl_community_username = 'RBNAdminSP'
        rayl_community_password = 'Spenard5@2022'
        current_user_email_id = partner.email
        partner_name = partner.name
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.match(regex, current_user_email_id):
            _logger.info("Email is not a valid Email Address  : %r" % (current_user_email_id))
            # raise UserError("Email is not a valid Email Address " + str(current_user_email_id))
        elif partner_name == '':
            _logger.info("Name Cannot be empty")
            # raise UserError("Name Cannot be empty")
        else:
            _logger.info("In Else condition")
            # apptive_domain = obj.client_url.replace("http://", "https://")
            apptive_domain = 'https://'
            apptive_share_username = domain_name
            apptive_db_name = domain_name
            apptive_email = current_user_email_id
            apptive_name = partner_name
            apptive_password = 'P@ssword'
            payload = {'email': current_user_email_id}
            headers = {
                "Content-Type": "application/json"
            }
            req = requests.get(rayl_community_url, params=payload,
                               auth=(rayl_community_username, rayl_community_password))
            if req:
                _logger.info("Updating the client")
                # Update the client
                user_update_details = json.dumps({
                    "account": {
                        "email": apptive_email
                    },
                    "password": {
                        "newPassword": "P@ssword"
                    }
                })
                res = json.loads(req.content.decode("utf-8"))
                url_update = rayl_community_update_url + str(res['id'])
                req_up = requests.put(url_update, data=user_update_details, headers=headers,
                                      auth=(rayl_community_username, rayl_community_password))
            else:
                _logger.info("Creating the client")
                # insert the client
                user_insert_details = json.dumps({
                    "account": {
                        "username": apptive_name,
                        "email": apptive_email
                    },
                    "profile": {
                        "firstname": [
                            apptive_name
                        ],
                        "lastname": [
                            "-"
                        ]
                    },
                    "password": {
                        "newPassword": "P@ssword"
                    }
                })
                req_up = requests.post(rayl_community_update_url, data=user_insert_details, headers=headers,
                                       auth=(rayl_community_username, rayl_community_password))
            if req_up:
                _logger.info("Successfully created the client")
                res_up = json.loads(req_up.content.decode("utf-8"))
                _logger(res_up["message"])
            else:
                _logger.info("Having error while creating client")
                res_up = json.loads(req_up.content.decode("utf-8"))
                # raise UserError(res_up["message"])
                _logger.info("Error is....  : %r" % (res_up["message"]))

    def saas_createuser(self, partner_id, domain_name):
        _logger.info("We are ready to start automation process")

        saas_configuration = self.env['saas.configuration'].sudo().search([], limit=1)
        if saas_configuration:
            url = 'https://' + saas_configuration.url
            db = saas_configuration.db
            username = saas_configuration.username
            password = saas_configuration.password
            invoice_product = saas_configuration.invoice_product
            server_id = saas_configuration.server_id
            plan_id = saas_configuration.plan_id

            partner = self.env['res.partner'].sudo().search([('id', '=', partner_id)], limit=1)
            # if partner.bought_membership:
            #     plan_id = 7
            _logger.info(
                "SaaS Configuration: url=%r, db=%r, username=%r, password=%r, invoice_product=%r, server_id=%r,"
                " plan_id=%r " % (url, db, username, password, invoice_product, server_id, plan_id))

            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            partner = ''
            contract_id = ''
            saas_client_domain = ''
            sale_obj = self.env['sale.order'].sudo().search([('partner_id', '=', partner_id)], limit=1)
            # sale_obj = self.env['sale.order'].sudo().search([('id', '=', 374)], limit=1)
            db_template = 'template_rayl_tid_1'

            if sale_obj.amount_total == 59.95:
                db_template = 'template_apptive_pro_tid_7'
                plan_id = 7

            if partner_id:
                partner = self.env['res.partner'].sudo().search([('id', '=', partner_id)], limit=1)
            if partner:
                try:
                    if not partner.is_saas_user:
                        saas_user_id = models.execute_kw(db, uid, password, 'res.users', 'create',
                                                         [{'name': partner.name,
                                                           'login': partner.email,
                                                           'groups_id': [(6, 0, [9])]}])
                        partner.write({'is_saas_user': True,
                                       'saas_user_id': saas_user_id})
                        _logger.info("SaaS User is created in RAYL And User Id is : %r" % (saas_user_id))
                    else:
                        saas_user_id = partner.saas_user_id
                        _logger.info("SaaS User is already created in RAYL And User Id is : %r" % (saas_user_id))
                    saas_partner_id = models.execute_kw(db, uid, password,
                                                        'res.users', 'search_read',
                                                        [[['id', '=', saas_user_id]]],
                                                        {'fields': ['name', 'partner_id'], 'limit': 1})
                    for a_dict in saas_partner_id:
                        saas_partner = (a_dict["partner_id"][0])
                        saas_partner_update = models.execute_kw(db, uid, password, 'res.partner', 'write',
                                                                [[saas_partner], {
                                                                    'email': partner.email}])
                    if not partner.is_saas_contract:
                        contract_id = models.execute_kw(db, uid, password, 'saas.contract', 'create',
                                                        [{
                                                            'partner_id': saas_partner or False,
                                                            'invoice_product_id': invoice_product,
                                                            'pricelist_id': 1,
                                                            'contract_rate': sale_obj.amount_total,
                                                            'contract_price': sale_obj.amount_total,
                                                            'total_cost': sale_obj.amount_total,
                                                            'server_id': server_id,
                                                            'plan_id': plan_id,
                                                            'auto_create_invoice': True,
                                                            'domain_name': domain_name,
                                                            'start_date': date.today(),
                                                            'saas_module_ids': [(6, 0,
                                                                                 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                                                                                  13, 14, 15])],
                                                            'db_template': db_template,
                                                            'from_backend': True, }])
                        partner.write({'is_saas_contract': True,
                                       'saas_contract_id': contract_id})
                        _logger.info("SaaS Contract is created in RAYL And User Id is : %r" % (saas_user_id))
                    else:
                        contract_id = partner.saas_contract_id
                        _logger.info("SaaS Contract is Already created in RAYL And Contract Id is : %r" % (contract_id))

                    if not partner.is_saas_client:
                        client_instance = models.execute_kw(db, uid, password, 'saas.contract', 'create_saas_client',
                                                            [int(contract_id)])
                        saas_client_details = models.execute_kw(db, uid, password,
                                                                'saas.client', 'search_read',
                                                                [[['saas_contract_id', '=', contract_id]]],
                                                                {'fields': ['name', 'database_name'], 'limit': 1})
                        for a_dict in saas_client_details:
                            saas_client_domain = (a_dict["database_name"])
                        if saas_client_domain:
                            partner.write({'is_saas_client': True,
                                           'saas_url': saas_client_domain if saas_client_domain else False})
                            _logger.info(
                                "SaaS Contract is confirmed and SaaS Client is created in RAYL And Client URL is : %r" % (
                                    saas_client_domain))
                            if sale_obj.amount_total == '59.95':
                                _logger.info("Sale amount is 59.95 and ready to sync rayl community user")
                                self.synch_rayl_community_user(partner, domain_name)
                                _logger.info("Completed RAYL USER is SYNC with Community...........   :")

                except Exception as e:
                    if not partner.is_saas_client:
                        saas_client_details = models.execute_kw(db, uid, password,
                                                                'saas.client', 'search_read',
                                                                [[['saas_contract_id', '=', contract_id]]],
                                                                {'fields': ['name', 'database_name'], 'limit': 1})
                        for a_dict in saas_client_details:
                            saas_client_domain = (a_dict["database_name"])
                        if saas_client_domain:
                            partner.write({'is_saas_client': True,
                                           'saas_url': saas_client_domain if saas_client_domain else False})
                            _logger.info(
                                "Log From Exception: SaaS Contract is confirmed and SaaS Client is created in RAYL And "
                                "Client URL is : %r" % (saas_client_domain))
                            if sale_obj.amount_total == '59.95':
                                _logger.info("Sale amount is 59.95 and ready to sync rayl community user")
                                self.synch_rayl_community_user(partner, domain_name)
                                _logger.info("Completed RAYL USER is SYNC with Community...........   :")
                    _logger.info(
                        "Exception Is : %r" % (e))
            else:
                _logger.info("Sale order amount is not equal to 59.95........................")
        else:
            raise UserError(_("SaaS Configuration is not setup, Please setup first and then automation will work."))

    def saas_instance_login(self):
        login_url = "rayl.website"
        return {
            'type': 'ir.actions.act_url',
            'url': login_url,
            'target': 'new',
        }