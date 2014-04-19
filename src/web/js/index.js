function load_business_main_pane(data) {
	var id = data.id;
	get_schedule(id, $("#data_subpane"), false);
	$("#main_pane").show();
}

function load_client_main_pane(data) {
	$("#control_subpane").append("<p>What service would you like?</p>");
	var select = $('<select></select>');
	select.append("<option>Select</option>");
	$.ajax({
		type: "GET",
		url: "http://localhost:5000/api/v1.0/business",
		mimeType: "application/json"
	}).done(function(data) {
		// Populate data
		$.each(data, function(index, biz) {
			var opt = $("<option>" + biz.name + "</option>");
			opt.attr('biz_id', biz.id);
			select.append(opt);
		});
	});
	select.change(function() {
		get_schedule($(this).find(":selected").attr('biz_id'), $("#data_subpane"), true);
	})
	$("#control_subpane").append(select);
	$("#main_pane").show();
}

function get_schedule(id, element, showOpenOnly) {
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
		var table = this;
		this.ref = $("<table class='table-bordered table-hover'></table>"); 
		table.ref.append("<tr><th class='col-md-8'><b>Time</b></th><th class='col-md-4'><b>State</b></th><th></th></tr>"); // Insert table header
		$.each(timeslot.sort(), function(index, key) {
			if (showOpenOnly == true) {
				if (schedule[key] == "OPEN" ) {
					var time = "<td class='col-md-8'>" + key + "</td>";
					var state = "<td class='col-md-4'>" + schedule[key] + "</td>";
					var row = "<tr>" + time + state + "</tr>";
					table.ref.append(row);
				}
			} else {
				var time = "<td class='col-md-8'>" + key + "</td>";
				var state = "<td class='col-md-4'>" + schedule[key] + "</td>";
				// don't need it right now: var cancel_btn = 
				var row = "<tr>" + time + state + "</tr>";
				//$("#schedule_table").append(row);
				table.ref.append(row);
			}
		});
		// Post processing
		element.empty(); // Clean out old data efore inserting new data.
		if (table.ref.find("tr").length == 1) {
			// No data found
			element.append("<p>Sorry, no available appointments found.</p>");
		} else {
			element.append(table.ref);
		}
	});
}

function load_header_pane(data) {
	var header = "<h3>Welcome <strong>" + data.name + "!</strong></h3>";
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
