
$(document).on('change','#payment_option',function(){
       if($(this).val()=='electronic_funds_transfer'){
         $('#electronic_funds_transfer').show();
         $('#credit_card').hide();
       }else if($(this).val()=='credit_card'){
         $('#electronic_funds_transfer').hide();
         $('#credit_card').show();
       }
});

$(document).on('change','#bank_account_type',function(){
   if($(this).val()=='Business'){
        $('#company_name_form_group').show();
        $('#company_name').attr('required',true);
        $('#company_name').attr('disabled',false);
   }else{
       $('#company_name').attr('required',false);
       $('#company_name').attr('disabled',true);
       $('#company_name_form_group').hide();
   }
})

//this.$buttons.on('click', '.o_form_button_delete', this._onDeleteRecord.bind(this));

$('#card_number').focusout(function(){
         var card_number = this.value.replace(/\s+/g,'');
         var pattern = new RegExp("(^4[0-9]{12}([0-9]{3})?$)|(^5[1-5][0-9]{14}$|^2[0-9]{15}$)|(^3[47][0-9]{13}$)|(^65[4-9][0-9]{13}|64[4-9][0-9]{13}|6011[0-9]{12}|(622(12?[6-9]|1[3-9][0-9]|[2-8][0-9][0-9]|9[01][0-9]|92[0-5])[0-9]{10})$)");
         var result = pattern.test(card_number);
//         if(result==false)
//         {
//            alert("Invalid Card Number.");
////            this.setCustomValidity("Invalid Card Number");
//         }
//         else
//         {
//            alert("Valid Card Number.")
////            this.setCustomValidity("");
//         }
         var cvv = document.getElementById("card_code");
         var pattern = new RegExp("^3[47][0-9]{13}$");
         var result = pattern.test(card_number);
         if(result == true){
             cvv.setAttribute("maxlength", "4");
             cvv.setAttribute("minlength", "4");
         }
         else{
             cvv.setAttribute("maxlength", "3");
             cvv.setAttribute("minlength", "3");
         }
//         ^4[0-9]{12}([0-9]{3})?$ //Visa Card Regex
        });

//function nextPrev(val){
//var branch_transit_number = $('#branch_transit_number').val();
//var bank_account_number = $('#bank_account_number').val();
//var confirm_bank_account_number = $('#confirm_bank_account_number').val();
//if(val==1){
//    if(branch_transit_number!='' && bank_account_number!='' && confirm_bank_account_number!=''){
//        if(bank_account_number==confirm_bank_account_number){
//            $('.tab1').hide();
//            $('.tab2').show();
//        }else{
//            alert("Confirm Account does not match");
//        }
//    }else{
//        alert("Please Fill the Detail and try again");
//    }
//}
//if(val==2){
//    $('.tab2').hide();
//    $('.tab1').show();
//    }
//}

odoo.define('billing_setting.branch_transit',function(require){
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');

var _t = core._t;

$('#bank_id').select2({

placeholder: "Branch Transit Number",

});

console.log(1)
$(document).on('change', 'select[name="bank_id"]', function() {

    if (!$("#bank_id").val()) {
            return;
        }

    if($("#bank_id option:selected").text().trim()=='Other'){
        $('#bank_name_form_group').show();
        $('#branch_default').hide();
        $('#branch_other').show();
        $('#other_bank_name').attr('required',true);

        $('#branch_transit_number_sl').attr('required',false);
        $('#branch_transit_number_sl').attr('disabled',true);

        $('#branch_transit_number_in').attr('disabled',false);
        $('#branch_transit_number_in').attr('required',true);
         console.log(2)
    }else{

         $('#branch_transit_number_in').attr('required',false);
         $('#branch_transit_number_in').attr('disabled',true);

         $('#branch_transit_number_sl').attr('required',true);
         $('#branch_transit_number_sl').attr('disabled',false);

         ajax.jsonRpc("/bank_transit",'call',{
                    id:$("#bank_id").val(),
                }).then(function (data) {

                var branch_transit_number = $("#branch_transit_number_sl");

                if (branch_transit_number.data('init')===0 || branch_transit_number.find('option').length===1) {
                   if (data) {

                    branch_transit_number.html('');
                    branch_transit_number.append('<option value="">Select Branch Transit Number</option>')
                    _.each(data, function (x) {
                        var opt = $('<option>').text(x['transit_number'] + ' - ' + x['address_string'])
                            .attr('value', x['transit_number'])
                        branch_transit_number.append(opt);
                    });
                    $('#bank_name_form_group').hide();
                    $('#branch_other').hide();
                    $('#branch_default').show();
                    $('#other_bank_name').attr('required',false);

                    branch_transit_number.select2({
                        placeholder: "Branch Transit Number",
                    });
                } else {
                    branch_transit_number.val('').parent('div').hide();
                }
                branch_transit_number.data('init', 0);
                }else {
                branch_transit_number.data('init', 0);
            }
         });
        }
    });

//    $(document).on('change', '#branch_transit_number_sl', function() {
//             $('.branch_details').show();
//             if (!$("#branch_transit_number_sl").val()) {
//                    return;
//                }
//             $('#branch_address1').val("10705 West Side drive");
//             $('#branch_address2').val("Grande Prairie");
//             $('#branch_city').val('Fort McMurray');
//             $('#branch_province').val("AB T9H 2K5");
//             $('#branch_postal').val("Branch Postal");
//    });

});

odoo.define('billing_setting.user_details',function(require){
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');

var _t = core._t;
$(document).on('change', 'select[name="country_id"]', function() {

    if (!$("#country_id").val()) {
            return;
        }
        ajax.jsonRpc("/shop/country_infos/" + $("#country_id").val(),'call',{
                    mode: $("#country_id").attr('mode'),
                }).then(function (data) {
            // populate states and display
            var selectStates = $("select[name='state_id']");
            // dont reload state at first loading (done in qweb)
            if (selectStates.data('init')===0 || selectStates.find('option').length===1) {
                if (data.states.length || data.state_required) {
                    selectStates.html('');
                    _.each(data.states, function (x) {
                        var opt = $('<option>').text(x[1])
                            .attr('value', x[0])
                            .attr('data-code', x[2]);
                        selectStates.append(opt);
                    });
                    selectStates.parent('div').show();
                } else {
                    selectStates.val('').parent('div').hide();
                }
                selectStates.data('init', 0);
            } else {
                selectStates.data('init', 0);
            }
        });

    });
});