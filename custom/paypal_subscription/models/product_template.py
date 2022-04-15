from odoo import _, api, fields, models

class ProductProductPaypal(models.Model):
    _inherit = 'product.product'

    paypal_plan_id = fields.Char(string="Paypal Plan ID")
