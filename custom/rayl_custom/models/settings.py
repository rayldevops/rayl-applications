from odoo.exceptions import UserError
from odoo import models, fields,api,_
import random, string
import datetime

import logging
_logger = logging.getLogger(__name__)

class InheritResUsers(models.Model):
    _inherit = 'res.users'

    def _is_admin(self):
        res = super(InheritResUsers, self)._is_admin()
        return self._is_superuser() or self.has_group('base.group_erp_manager') or self.has_group('rayl_custom.saas_security_manager_group')
