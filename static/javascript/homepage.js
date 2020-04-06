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

$("#codelist").prepend("<option value=''></option>").val('');

function changeterm(value) {
	if (value.length == 0) document.getElementById("terms").innerHTML = "<option></option>";
	else {
		var list_of_terms = "";
		for (codelists in codelist_terms[value]) {
			list_of_terms += "<option>" + codelist_terms[value][codelists] + "</option>";
		}
		document.getElementById("terms").innerHTML = list_of_terms;
	}
}
