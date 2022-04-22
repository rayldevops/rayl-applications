from odoo import models, fields, api,_
from random import choice
from odoo.http import request


def create_hash():
    size = 32
    values = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    p = ''
    p = p.join([choice(values) for i in range(size)])
    app_id = request.env['ir.config_parameter'].sudo().get_param('jitsi.app_id')
    return f"{app_id}/{p}"


class JistiMeet(models.Model):
    _name = 'jitsi.meet'
    _description = 'RAYL Meeting'
    _order = 'date desc'
    _inherit = 'mail.thread'

    def _get_default_participant(self):
        result = []
        result.append(self.env.user.id)
        return [(6, 0, result)]

    name = fields.Char('Meeting Name', required=True)
    hash = fields.Char('Hash')
    date_formated = fields.Char(
        string='Date Formated',
        compute='_format_date', store=True)
    date = fields.Datetime('Date', required=True)
    date_delay = fields.Float('Duration', required=True, default=1.0)
    participants = fields.Many2many('res.users', string='Participant', required=True, default=_get_default_participant)
    url = fields.Char(string='URL to Meeting', compute='_compute_url')
    url_to_link = fields.Char(string='URL to link', compute='_compute_url', store=True)
    closed = fields.Boolean('Closed', default=False)
    current_user = fields.Many2one('res.users', compute='_get_current_user')
    domain = fields.Char(string='Domain', required=False, compute='_compute_domain')
    is_password_required = fields.Boolean(
        string='Is username and password required?',
        required=False, default=False)
    password = fields.Char(
        string='Password', default='',
        required=False)
    user = fields.Char(
        string='User', default='',
        required=False)

    def _compute_domain(self):
        for r in self:
            r.domain = self.env['ir.config_parameter'].sudo().get_param(
                'jitsi.meet_url',
                default='meet.jit.si')

    @api.depends()
    def _get_current_user(self):
        for rec in self:
            rec.current_user = self.env.user

    @api.model
    def create(self, vals):
        vals['hash'] = create_hash()
        res = super(JistiMeet, self).create(vals)
        return res

    def action_close_meeting(self):
        self.write({'closed': True})

    def action_reopen_meeting(self):
        self.write({'closed': False})

    def open(self):
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url',
                                                               default='http://localhost:8069')
        return {'name': 'RAYL MEET',
                'res_model': 'ir.actions.act_url',
                'type': 'ir.actions.act_url',
                'target': 'new',
                'url': url + "/meet/" + str(self.id)
                }

    @api.depends('name')
    def _compute_url(self):

        config_url = self.env['ir.config_parameter'].sudo().get_param(
            'jitsi_calendar.meet_url',
            default='https://meet.jit.si/')
        url_site = self.env['ir.config_parameter'].sudo().get_param('web.base.url',
                                                                    default='http://localhost:8069')
        for r in self:
            if not r.hash:
                r.hash = create_hash()
            if r.hash and r.name and r.id:
                r.url = config_url + r.hash
                r.url_to_link = url_site + "/meet/" + str(r.id)
                print(r.url)

    def send_mail(self):
        for record in self.participants:
            mail_content = _(
                '<div><p>You have been invited to a meeting</p>'
                ' <p>Please join us on  %s by clicking on the followin link: </p>'
                ' <p>'
                '<a href="%s">JOIN MEETING</a>'
                ' </p>')
            if self.is_password_required:
                mail_content = _(
                '<div><p>You have been invited to a meeting</p>'
                ' <p>Please join us on  %s by clicking on the followin link: </p>'
                ' <p>'
                '<a href="%s">JOIN MEETING</a>'
                ' </p>'
                '<p>Credentials </p>'
                ' <p>User: %s</p>'
                '<p>Password:  %s</p>'
                 '<p>Thank you,</p></div>') % (self.date_formated, self.url_to_link, str(self.user), str(self.password))
            else:
                mail_content +='<p>Thank you,</p></div>'
                mail_content = (mail_content) % (self.date_formated, self.url_to_link)
            main_content = {
                'subject': "RAYL Meet Invitation",
                'author_id': self.env.user.partner_id.id,
                'body_html': mail_content,
                'email_to': record.email,
            }
            self.env['mail.mail'].create(main_content).send()
        self.env['mail.mail'].process_email_queue()

    @api.depends('date')
    def _format_date(self):
        for part in self:
            if part.date:
                part.date_formated = fields.Datetime.from_string(part.date).strftime('%m/%d/%Y, %H:%M:%S')