function load_business_main_pane(data) {
	var id = data.id;
	$.ajax({
		type: "GET",
		url: "http://localhost:5000/api/v1.0/schedule",
		mimeType: "application/json",
		data: {id: id},
		dataType: "json"
	}).done(function(data) {
		// Populate data
		var schedule = data.schedule;
		var timeslot = [];
		for (var key in schedule) {
			if (schedule.hasOwnProperty(key)) {
				timeslot.push(key);
			}
		}
		$("#main_pane").append("<table id='schedule_table'></table>"); // Insert table element
		$("#schedule_table").append("<tr><th>Time</th><th>State</th><th></th></tr>"); // Insert table header
		$.each(timeslot.sort(), function(index, key) {
			var time = "<td>" + key + "</td>";
			var state = "<td>" + schedule[key] + "</td>";
			// don't need it right now: var cancel_btn = 
			var row = "<tr>" + time + state + "</tr>";
			$("#schedule_table").append(row);
		});
	});
}

function load_client_main_pane(data) {
	// Stub
}

function load_header_pane(data) {
	var header = "<p>Welcome " + data.name + "!</p>";
	$("#top_pane").append(header);
	$("#top_pane").show();
}

function logged_in(data) {
	// Hide login pane
	$("#login_pane").hide();
	// Show header pane
	load_header_pane(data);
	
	if (data.type == "business") {
		load_business_main_pane(data);
	} else {
		load_client_main_pane(data);
	}
}
function login() {
	var username = $("#username").val();
	var password = $("#password").val();
	$.ajax({
		type: "GET",
		url: "http://localhost:5000/api/v1.0/login",
		mimeType: "application/json",
		data: {username: username, password: btoa(password)},
		dataType: "json",
	}).done(function(data) {
		logged_in(data);
	});
}

$( document ).ready(function() {
	$("#login").click(login);
});
