/*!
 # -*- coding: utf-8 -*-
#################################################################################
 */

odoo.define('website_terms_conditions.enable_process_checkout_button', function(require) {
    "use strict";

var publicWidget = require('web.public.widget');

publicWidget.registry.WebsiteTermsAndConditions = publicWidget.Widget.extend({
    selector: '#wrapwrap:has(#process_checked,#agree_terms_checked)',
    events: {
                    'click .custom-control': '_onClickEnableProcessCheckout',
                    'click .field-agree-terms': '_onClickEnableSignUp',
    },

    _onClickEnableProcessCheckout: function () {
            var checkbox = $('#process_checked:checkbox:checked').length;
            if (checkbox>0) {
                    this.$('.o_cart_process_checkout').removeClass('disabled');
                }
                else {
                    this.$('.o_cart_process_checkout').addClass('disabled');
                }

            if (checkbox>0) {
                    this.$('.o_cart_summary_process_checkout').removeClass('disabled');
                }
                else {
                    this.$('.o_cart_summary_process_checkout').addClass('disabled');
                }
                },

    _onClickEnableSignUp: function () {
            var checkbox = $('#agree_terms_checked:checkbox:checked').length;
            console.log('test',checkbox)
            if (checkbox>0) {
                    this.$('.o_sign_up_button').removeClass('disabled');
                }
                else {
                    this.$('.o_sign_up_button').addClass('disabled');
                }
                },
});
});
