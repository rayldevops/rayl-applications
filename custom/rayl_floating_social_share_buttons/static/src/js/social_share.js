odoo.define('rayl_floating_social_share_buttons.social_share', function (require) {
'use strict';

var ajax = require('web.ajax');
var core = require('web.core');
var publicWidget = require('web.public.widget');
var rpc = require("web.rpc");
var qweb = core.qweb;

var registry = publicWidget.registry;

registry.websiteSharePopUp = publicWidget.Widget.extend({
    selector: '#wrapwrap',
    xmlDependencies: ['/rayl_floating_social_share_buttons/static/src/xml/website_share_buttons.xml'],
    events: {
        'click .oe_share_call': '_onButtonsShare',
        'click .ssButtonsBar': '_bindSocialEventBar',
    },
    _bindSocialEventBar: function () {
        var self = this
        var social = ''
        $('body').on('click', 'i.ssButtonsBar', function(){
            //3.3 Evento para la function compartir final
             social = $(this).data('social');
             self._clickButtonMedia(social)
        });
    },

    _onMouseEnterTitle: function () {
        var social = this.$el.data('social');
        //this.socialList = social ? social.split(',') : ['facebook', 'twitter', 'linkedin'];
        //this.hashtags = this.$el.data('hashtags') || '';
        console.log('Data-social', social)
       // this._render();
        //this._bindSocialEvent();
    },
    //3.1 Maneja los evento que ejecutaran los boton dentro del PopUp
    _bindSocialEventPopUp: function () {
        var self = this
        var social = ''
        $('body').on('mouseenter', '.ssButtons', function(){
            // 3.2 Llama y pasa parametros al popup Title red Social
            social = $(this).data('social');
            // TO-DO function java sccrtp para cambiar a minus y sin espacio data-social
            //self._overButtons(social)
        });
        $('body').on('click', '.ssButtons', function(){
            //3.3 Evento para la function compartir final
            social = $(this).data('social');
            self._clickButtonMedia(social)
        });
    },
    //3.2.1 Function Title dinamico
    _overButtons: function (social) {
        var button = this.$el.find('.ssButtons');
        //this.$el.find('a.ssButtons')
       $('a[data-social=' + social + ']').popover({
            content: qweb.render('rayl_floating_social_share_buttons.social_hover', {name_media: social}),
            placement: 'bottom',
            container: 'body',
            html: true,
            trigger: 'manual',
            animation: false,
        }).popover("show");

        $('.modal-body').on('mouseleave', '.ssButtons', function () {
            var self = this;
            setTimeout(function () {
                if (!$(".popover:hover").length) {
                    $(self).popover('dispose');
                }
            }, 200);
        });


    },

    _openScreanPopupWin: function(pageURL, pageTitle, popupWinWidth, popupWinHeight) {
            var left = (screen.width - popupWinWidth) / 2;
            var top = (screen.height - popupWinHeight) / 4;

            var myWindow = window.open(pageURL, pageTitle,
                    'menubar=no, toolbar=no, resizable=yes, scrollbar=yes, width=' + popupWinWidth
                    + ', height=' + popupWinHeight + ', top='
                    + top + ', left=' + left);
    },

    _clickButtonMedia: function(social){
        var url = this.$el.data('urlshare') || document.URL.split(/[?#]/)[0];
        var title = document.title.split(" | ")[0];
        var self = this;
        var image = $('meta[property="og:image"]').attr("content");

        $('body').off('click', 'i.ssButtonsBar')
        this._rpc({
            route: '/web/dataset/call_share_floating',
            args: [url, title, social, image],
            kwargs: {},
            model: 'share.social.list',
            method: 'parameter_social_url',
        }).then(function (result) {
        console.log("twitter")
           self._openScreanPopupWin(result,  'Share Content', 630, 500);
        });
    },

    //2.1-Render html de la ventana donde sale todos los botones

    _renderPopUpSocial: function (sociaList) {
        var self = this;
        var socialList = sociaList;

        $('body').append(qweb.render('rayl_floating_social_share_buttons.all', {medias: socialList}));
        $('#gtica_social_share_modal').modal('show');
    },
    // 1.- Llama metodo python para traer array con todas las redes sociales
    _onButtonsShare: function (e){
        var self = this;

        rpc.query({
            route: '/web/dataset/call_share_floating',
            args: [],
            kwargs: {},
            method: 'social_list',
            model: 'share.social.list',
        }).then(function (result) {
            // 2.- Activa y pasa paramentros al Render Html PopUp de todo los botonoes
            self._renderPopUpSocial(result)
            // 3.- Crea en DOM envento para los botones del PopUp
            self._bindSocialEventPopUp();
        });
    },
});


return {
    Widget: publicWidget.Widget,
    registry: registry,
};
});