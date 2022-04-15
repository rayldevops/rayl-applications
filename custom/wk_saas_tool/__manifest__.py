{
  "name"                 :  "Saas Tool",
  "summary"              :  "Saas Tool",
  "category"             :  "Extra",
  "version"              :  "2.1.1",
  "sequence"             :  1,
  "author"               :  "Planet Odoo",
  "description"          :  """Saas tools""",
  "depends"              :  [
                                'base', 'web', 'mail'
                            ],
  "data"                  : [
                              'views/template.xml',
                              'data/email_templates.xml',
                              'data/ir_config_parameter.xml',
                            ],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  True,
}
