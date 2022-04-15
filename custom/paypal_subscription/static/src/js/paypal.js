
paypal.Buttons({
  //var plan_id = 'P-5CL39556TL0153457MBAP6JI';
  createSubscription: function(data, actions) {
    var plan_id =  document.getElementById('product_plan_id').value;
    return actions.subscription.create({
      'plan_id': plan_id
    });
  },

  onApprove: function(data, actions) {
    console.log(data)
    var plan_id =  document.getElementById('product_plan_id').value;
    var self = this;
      $.ajax({
        type: 'POST',
        url: '/confirm_subscription',
        dataType: 'json',
        data : {'datas':data,'plan_id':plan_id}
        });
    alert('You have successfully created subscription ' + data.subscriptionID);
  }
}).render('#paypal-button-container');
