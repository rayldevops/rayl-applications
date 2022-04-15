/*!
 # -*- coding: utf-8 -*-
#################################################################################
 */

odoo.define('jitsi_call_meets.theme_manon', function(require) {
    "use strict";

    var session = require('web.session');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;
    var session = require('web.session');
    var ThemeSlider = Widget.extend({

        template: 'ThemeSlider',
        events: {
            'click .o_create_meeting': '_onClickCreateMeeting',
            'click .o_join_meeting': '_onClickJoinMeeting',
//           "click .theme_item": 'change_theme',
        },

         _onClickCreateMeeting: function (event) {
//                var $parent = $(event.currentTarget);
//                var meeting_id_url = $parent.data('meeting_id_url');
                var meeting_id_url = document.getElementById('meeting_id_url').value;
                var meeting_date_time = document.getElementById('meeting_date_time').value;
                var meeting_date = meeting_date_time.replace('T',' ')
//                var domain = []
//                var fields = ['name','id']
//                var users_datas=({
//                model: 'res.users',
//                method: 'search_read',
//                args: [domain, fields]
//                })
//                var users = users_datas.then(function(res){
//                  for (i in res){
//                        console.log(i.name)
//                        }
//                    return res[0].url_to_link;
//                  })
//                .all().then(function(temp)
//                        {
//                        for (i in temp){
//                        console.log(i.name)
//                        }
//                {console.log('temp',temp)}
//                 var invite_user = temp.then(function(res){
//
//                        console.log('res',res)
//                 if (res[0].participants) {
//                       'name':meeting_id_url;
//                       }
//                  })

              return this._rpc({
              model: 'jitsi.meet',
              method: 'create',
              args: [
                  {'name':meeting_id_url,'hash':'','date':meeting_date,'date_formated':meeting_date}
              ]
          })
        },


        _onClickJoinMeeting(ev) {
//        var $parent = $(event.currentTarget).closest('tr');
//         var meeting_id_url = $parent.data('meeting_id_url');
           var meeting_id_url = document.getElementById('meeting_id_url').value;
           var domain = [['name', '=', meeting_id_url]]
           var fields = ['url_to_link']
         var meeting = this._rpc({
              model: 'jitsi.meet',
              method: 'search_read',
              args: [domain, fields],

          });
          //var meet = $.parseJSON(meeting);
          var meet_url = meeting.then(function(res){
          if (res[0].url_to_link) {
                window.open(res[0].url_to_link, '_new');
            }
            return res[0].url_to_link;
          })

        },

    });

    if ( session.is_system ) {
        SystrayMenu.Items.push(ThemeSlider);
    }

});
$(document).ready(function() {
    $('.invite_user').select2();
});
