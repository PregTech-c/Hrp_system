//$(function() {
//  $("#addMore").click(function(e) {
//    e.preventDefault();
//    $("#fieldList").append("<li>&nbsp;</li>");
//    $("#fieldList").append("<li><input type='text' name='{{ dform.full_name }}' placeholder='Name' /></li>");
//    $("#fieldList").append("<li><input type='text' name='phone[]' placeholder='Phone' /></li>");
//    $("#fieldList").append("<li><input type='text' name='email[]' placeholder='E-Mail' /></li>");
//  });
//});

(function() {
   var button=document.getElementById("add-user");
   button.addEventListener('click', function(event) {
      event.stopPropagation();
      event.preventDefault();
      var cln = document.getElementsByClassName("user")[0].cloneNode(true);
      document.getElementById("users").insertBefore(cln,this);
      return false;
   });
})();
