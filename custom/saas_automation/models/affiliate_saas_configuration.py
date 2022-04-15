from odoo import _, api, fields, models


class SaasConfiguration(models.Model):
    _name = 'saas.configuration'
    _rec_name = 'url'

    url = fields.Char('URL')
    db = fields.Char('Database Name')
    username = fields.Char('Username')
    password = fields.Char('Password')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('connected', 'Connected'),
    ], string='Status', readonly=True, default='draft')
    invoice_product = fields.Char('Invoice Product Id')
    server_id = fields.Char('SaaS Server Id')
    plan_id = fields.Char('SaaS Plan Id')

    def action_check_connectivity(self):
        print('Test check connectivity')
        self.write({'state': 'connected'})

    def action_reset_draft(self):
        print('Test reset to draft')
        self.write({'state': 'draft'})
