// Pragnesh Code Start // 
//       console.log(variant.id, 'pragnesh');
var shopdata;
jQuery.each(Shopify, function(i,e){
  if(i == 'shop'){
    shopdata = e;
  }
});
console.log(customer, "customer is");
$.ajax({
  url:'https://raffle.pagekite.me/check_raffle_activation',
  type:'get',
  data:{'variant':variant.id, 'shop':shopdata},
  success: function(response) {
    if (response != {}) {
      if (response.data) {
        $('.product-form__item--submit').hide();
        $('.selector-wrapper').append("<div id='raffle'><button id='raffle_id' name='raffle_id' value='"+response.data.raffle_id+"'>Raffle</button></div>");
      }
      else{
        $('.product-form__item--submit').show();
        $("#raffle").remove();
        alert(response.error);
      }
    }
  }
})
// Pragnesh Code End //