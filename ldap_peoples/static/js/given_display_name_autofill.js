/*
 * @author Giuseppe De Marco <giuseppe.demarco@unical.it>
 */
/*jslint browser:true */
function input_by_name(nome){
    return "input[type='text'][name='" + nome +"']"
}

django.jQuery( document ).ready(function() {

    django.jQuery(input_by_name("cn")).change(function() {
      var value = django.jQuery(this).val();
      // console.log(value);
      django.jQuery(input_by_name("givenName")).val(value);
      django.jQuery(input_by_name("displayName")).val(value);
    });

    django.jQuery(input_by_name("sn")).change(function() {
      var value = django.jQuery(this).val();
      // console.log(value);
      django.jQuery(input_by_name("displayName")).val(django.jQuery(this).val() + ' ' + value);
    });

})
