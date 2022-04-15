# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Multi-Level Marketing",
  "summary"              :  """Multi-Level Marketing extension for odoo Affiliate Management.""",
  "version"              :  "1.1.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "maintainer"           :  "Anuj Kumar Chhetri",
  "website"              :  "https://store.webkul.com/Odoo-Multi-Level-Marketing.html",
  "description"          :  """MLM customization extension for the Affiliate Management""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=affiliate_management_mlm&lifetime=90&lout=1&custom_url=/",
  "depends"              :  [
                             'base',
                             'affiliate_management',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'data/admin_affiliate.xml',
                             'data/sequence_view.xml',
                             'data/default_mlm_configuration.xml',
                             'wizard/select_parent_views.xml',
                             'wizard/custom_dialog_box_views.xml',
                             # 'views/affiliate_templates.xml',
                             'views/signup_templates.xml',
                             'views/membership_templates.xml',
                             # 'views/index_templates.xml',
                             'views/website_sale_order.xml',
                             'views/header_templates.xml',
                             'views/mlm_configuration_views.xml',
                             'views/res_partner_views.xml',
                             'views/affiliate_management_views.xml',
                             'views/about_templates.xml',
                             'views/report_templates.xml',
                             'views/payment_templates.xml',
                             'views/tool_templates.xml',
                             'views/affiliate_user_nav.xml',
                             'views/mlm_tree_templates.xml',
                             'views/mlm_bonus_templates.xml',
                             'views/account_invoice_views.xml',
                             'views/mlm_payment_templates.xml',
                             'views/upgrade_membership_templates.xml'
                            ],
  "demo"                 :  ['data/demo_mlm_data.xml'],
  "images"               :  ['static/description/Multi-Level-Marketing-Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  99,
  "currency"             :  "USD",
}
