from odoo import _, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_terms_and_conditions = fields.Boolean('Show Terms And Conditions')
    is_terms = fields.Boolean('Terms and Conditions')
    title = fields.Text('Title')
    label = fields.Text('Label')
    terms_and_conditions = fields.Html(string='Terms & Conditions', translate=True)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            is_terms_and_conditions=self.env['ir.config_parameter'].sudo().get_param(
                'website_terms_conditions.is_terms_and_conditions'),
            title=self.env['ir.config_parameter'].sudo().get_param(
                'website_terms_conditions.title'),
            label=self.env['ir.config_parameter'].sudo().get_param(
                'website_terms_conditions.label'),
            terms_and_conditions=self.env['ir.config_parameter'].sudo().get_param(
                'website_terms_conditions.terms_and_conditions'),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        field1 = self.is_terms_and_conditions and self.is_terms_and_conditions or False
        field2 = self.title and self.title or False
        field3 = self.label and self.label or False
        field4 = self.terms_and_conditions and self.terms_and_conditions or False

        param.set_param('website_terms_conditions.is_terms_and_conditions', field1)
        param.set_param('website_terms_conditions.title', field2)
        param.set_param('website_terms_conditions.label', field3)
        param.set_param('website_terms_conditions.terms_and_conditions', field4)


    # @api.onchange('is_terms_and_conditions')
    # def _onchange_partner_id(self):
    #     # attachments = []
    #     # IrAttachment = self.env['ir.attachment']
    #     for company in self:
    #
    #         terms_and_conditions = company.search([
    #             # ('res_model', '=', 'res.company'),
    #             # ('type', '=', 'binary'),
    #             # ('res_id', '=', company.id),
    #             ('is_terms_and_conditions', '=', True),
    #         ])
    #
    #         for document in terms_and_conditions:
    #             if document not in company.terms_and_conditions:
    #                 document.unlink()
    #
    #         # for document in company.terms_and_conditions:
    #         #     if document not in terms_and_conditions:
    #         #         language_id = document.language_id.id if \
    #         #             document.language_id else False
    #         #         attachments.append(IrAttachment.create({
    #         #             'res_model': 'res.company',
    #         #             'name': document.name,
    #         #             'datas': document.datas,
    #         #             'is_terms_and_conditions': True,
    #         #             'language_id': language_id,
    #         #             'res_id': company.id,
    #         #             'type': 'binary',
    #         #         }))