from odoo import api, fields, models
import odoo.release
import odoo.sql_db
import odoo.tools
from odoo.sql_db import db_connect
import threading
import werkzeug.utils
from odoo.http import request


class ResUsers(models.Model):
    _inherit = 'res.users'

    login_as_user_id = fields.Many2one('res.users', 'Login as')

    def login_as(self,):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/',
            'target': 'new',
        }
        # db_name = getattr(threading.currentThread(), 'dbname', None)
        # db = odoo.sql_db.db_connect(db_name)
        # login = self.login_as_user_id.login
        # with db.cursor() as cr:
        #     query = """SELECT login,password FROM res_users where login = %s"""
        #     cr.execute(query, list(login.split(' ')))
        #     rs = cr.dictfetchall()
        #     return {
        #         'type': 'ir.actions.act_url',
        #         'url': '/web/session/logout',
        #         'target': 'new ',
        #         }
            # return http.request.render('/web/login', {'users': login})
            # self.write({'login_as_user_id': False})
            # request.redirect('/web/session/logout')
        #     return {
        #         'type': 'ir.actions.act_url',
        #         'url': '/web/login ',
        #         'target': 'new',
        #     }

    def logout_as(self):
        return self.write({'login_as_user_id': False})
