# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models, _
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class PaymentInherit(models.Model):
    _inherit = 'payment.transaction'

    stripe_subscription_id = fields.Text(string="Stripe Subscription id")
