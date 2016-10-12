$(document).ready (function(){
  // Close the volunteer registration alert 2 seconds after it is displayed
  $("#success-alert").alert();
  window.setTimeout(function() {
    $("#success-alert").alert('close');
  }, 2000);

 });
