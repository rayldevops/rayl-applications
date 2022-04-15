import werkzeug

from odoo import models
from odoo.http import request
from odoo.modules.module import get_resource_path, get_module_path


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    # @classmethod
    # def _match(cls, path_info, key=None):
    #     return cls.routing_map().bind_to_environ(request.httprequest.environ).match(path_info=path_info,
    #                                                                                 return_rule=True)

    @classmethod
    def _website_enabled(cls,path_info, key=None):
        try:
            func, arguments = cls._match()
            return func.routing.get('website', False)
        except werkzeug.exceptions.NotFound:
            return True

    # @classmethod
    # def _dispatch(cls):
    #     if cls._website_enabled():
    #         if not request.uid and request.context.get('uid'):
    #             user = request.env['res.users'].browse(request.context['uid'])
    #         else:
    #             user = request.env.user
    #         if user:
    #             request.uid = user.login_as_user_id.id or user.id
    #     return super(Http, cls)._dispatch()
