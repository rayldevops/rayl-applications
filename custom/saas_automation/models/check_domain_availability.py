from odoo import _, api, fields, models
import xmlrpc
import xmlrpc.client
from odoo.exceptions import UserError
from . pg_query import PgQuery

class SaasDomainCheck(models.Model):
    _name = 'saas.domain.check'

    def saas_domain_check(self, domain_name):
        saas_configuration = self.env['saas.configuration'].sudo().search([], limit=1)
        if saas_configuration:
            url = 'https://' + saas_configuration.url
            db = saas_configuration.db
            username = saas_configuration.username
            password = saas_configuration.password
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            try:
                saas_client = models.execute_kw(db, uid, password, 'saas.client', 'search_read',
                                                 [[['database_name', '=', domain_name]]],
                                                        {'fields': ['name'], 'limit': 1})
                print(saas_client)
                if saas_client:
                    return True
                else:
                    return False
            except Exception as e:
                print(e)
        else:
            raise UserError(_("SaaS Configuration is not setup, Please setup first and then automation will work."))

    def login_to_client_instance(self):
        for obj in self:
            host_server, db_server = obj.saas_contract_id.server_id.get_server_details()
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