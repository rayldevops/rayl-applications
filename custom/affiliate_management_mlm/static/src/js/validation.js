odoo.define('affiliate_management.validation-mlm',function(require){
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');

var _t = core._t;



$(document).ready(function() {
    $('#ref-code-signup-checkbox').on('click',function(){
        if(this.checked){
        $('#key-inp').css('display','');
        $('#aff_key').attr('required','True');
        }
        else{
            $('#key-inp').css('display','none');
            $('#aff_key').removeAttr('required');
            $('#aff_key').val('');
            $('#aff_ref_key_er').css('display','none');
            $('#aff_key_label').css('color','');
            $('#aff_key').css('border-color','');
        }

      });

      $(document).on('click',"#by_mlm",function(e){
            ajax.jsonRpc("/affiliate/check-affiliate",'call')
            .then(function(response){
                if (!response){
                    $('#en_f').css('display','');
                }
                else{
                  window.location.assign(response);
                }

            })
            .catch(function(result){
                console.log('-----fail--------');
            });

            });

            $(document).on('click',"#by_mlm_upgrade",function(e){
            ajax.jsonRpc("/affiliate/check-upgrade",'call')
            .then(function(response){
                if (!response){
                    $('#en_f').css('display','');
                }
                else{
                  window.location.assign(response);
                }

            })
            .catch(function(result){
                console.log('-----fail--------');
            });

            });

            $(document).on('click',"#by_mlm_bundle",function(e){
            ajax.jsonRpc("/affiliate/check-bundle",'call')
            .then(function(response){
                if (!response){
                    $('#en_f').css('display','');
                }
                else{
                  window.location.assign(response);
                }

            })
            .catch(function(result){
                console.log('-----fail--------');
            });

            });

      $(document).on('submit',".oe_signup_form",function(e){
            if($('#ref-code-signup-checkbox').checked){
            e.preventDefault();
            var affi_ref_key = $("#aff_key").val()

            ajax.jsonRpc("/affiliate/signup-referal-key",'call',{
                    'affi_ref_key' : affi_ref_key
                })
            .then(function(response){

                if (response['response']){
                    $('#aff_key_label').css('color','');
                    $('#aff_key').css('border-color','');
                    $('#aff_ref_key_er').css('display','none');

                    window.location.assign("/affiliate/register");
                }

                else{
                    $('#aff_key_label').css('color','#d43a3a');
                    $('#aff_key').css('border-color','#de7575');
                    $('#aff_ref_key_er').css('display','');

                    $('#aff_ref_key_er').text(response['msg']);
                }

            }).fail(function(result){
                console.log('-----fail--------');
            });
            }

            });

      $(document).on('click',"#js_ref_code",function(e){
            var affi_ref_key = $("#aff_ref_key").val()

            ajax.jsonRpc("/affiliate/affiliate-referal-key",'call',{
                    'affi_ref_key' : affi_ref_key
                })
            .then(function(response){

                if (response == 2){
                    $("div.alert").attr('class','alert alert-success');
                    $("div.alert").html("Affiliate Referral code is Successfully submited.");
                    // $('div.alert').css('display','none');
                }
                else if (response == 1){
                    $("div.alert").attr('class','alert alert-warning');
                    $('#er_ref').css('display','');
                    $('#er_ref').css('color','#8a6d3b');
                    $("#er_ref").text("Provided Affiliate Referral code cannot be used. Provide another Referral code or one would be applied automatically by admin.");
                }
                else{
                    $("div.alert").attr('class','alert alert-danger');
                    $('#er_ref').css('display','');
                    $('#er_ref').css('color','#a94442');
                    $("#er_ref").text("Affilate Referral code is Incorrect.");
                }

                // if (data['status'] == "success"){
                //
                //     if (data['cookie']['c_oldkey']){
                //         document.cookie = data['cookie']['c_oldkey']+"=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/";
                //     }
                //
                //     document.cookie = data['cookie']['c_newkey']+"="+data['cookie']['c_value']+"; expires="+data['cookie']['expires']+"; path=/";
                //
                //     location.reload()
                //
                // }
                // else if (data['status'] == "again"){
                //     $("#msg").attr("class","alert alert-warning")
                //     $("#msg").text(data["msg"])
                // }
                // else{
                //     $("#msg").attr("class","alert alert-danger")
                //     $("#msg").text(data["msg"])
                // }

            }).fail(function(result){
                console.log('-----fail--------');
            });

        });

});
});
