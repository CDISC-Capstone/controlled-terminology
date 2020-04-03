$('#rangestart').calendar({
  type: 'date',
  endCalendar: $('#rangeend')
});

$('#rangeend').calendar({
  type: 'date',
  startCalendar: $('#rangestart')
});

$(document).ready(function() {
    $('.js-example-basic-single').select2();
});