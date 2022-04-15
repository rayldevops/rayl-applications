paypal.Buttons({

  createSubscription: function(data, actions) {

    return actions.subscription.create({

      'plan_id': 'P-5CL39556TL0153457MBAP6JI'

    });

  },


  onApprove: function(data, actions) {

    alert('You have successfully created subscription ' + data.subscriptionID);

  }


}).render('#paypal-button-container');