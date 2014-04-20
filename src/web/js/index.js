function load_business_main_pane(id) {
	//var id = data.id;
	get_schedule(id, $("#data_subpane"), false);
	get_business_queue(id, $("#control_subpane"));
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

function load_header_pane(data) {
	var header = $("<h3>Welcome <strong>" + data.name + "!</strong></h3>");
	header.attr('id', data.id); // TODO: In the future put this info in a cookie. 
	$("#top_pane").append(header);
	$("#top_pane").show();
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
					var time = $("<td class='col-md-4'>" + key + "</td>");
					var state = $("<td class='col-md-4'>" + schedule[key] + "</td>");
					var reserve_col = $("<td class='col-md-4'></td>");
					var reserve_btn = $("<button class='btn btn-primary btn-block'>Reserve</button>");
					reserve_btn.click(function() {
						var user_id = $("#top_pane").find("h3").attr("id"); // TODO: In the future, fetch from cookie.
						var business_id = id;
						var timeslot = key;
						register_apt(user_id, business_id, timeslot, $(this));
					});
					reserve_col.append(reserve_btn);

					var row = $("<tr></tr>");
					row.append(time);
					row.append(state);
					row.append(reserve_col);
					table.ref.append(row);
				}
			} else {
				var time = "<td class='col-md-8'>" + key + "</td>";
				var state = "<td class='col-md-4'>" + schedule[key] + "</td>";
				// don't need it right now: var cancel_btn = 
				var row = "<tr>" + time + state + "</tr>";
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

function register_apt(user_id, business_id, timeslot, caller) {
	$.ajax({
		type: "POST",
		url: "http://localhost:5000/api/v1.0/register_apt",
		mimeType: "application/json",
		data: {id: business_id, user: user_id, timeslot: timeslot},
		dataType: "json"
	}).done(function(data) {
		caller.removeClass('btn-primary');
		caller.addClass('btn-success');
		caller.attr('disabled', "disabled");
		caller.text("Submitted");
	});
}

function set_apt(id, user_id, timeslot, caller) {
	$.ajax({
		type: "POST",
		url: "http://localhost:5000/api/v1.0/set_apt",
		mimeType: "application/json",
		data: {id: id, user: user_id, timeslot: timeslot},
		dataType: "json"
	}).done(function(data) {
		caller.removeClass('btn-primary');
		caller.addClass('btn-success');
		caller.attr('disabled', "disabled");
		caller.text("Done");
	});
}

function get_business_queue(id, element) {
	$.ajax({
		type: "GET",
		url: "http://localhost:5000/api/v1.0/business_queue",
		mimeType: "application/json",
		data: {id: id},
		dataType: "json"
	}).done(function(data) {
		var table = this;
		this.ref = $("<table class='table-bordered table-hover'></table>"); 
		table.ref.append("<tr><th class='col-md-8'><b>Time</b></th><th class='col-md-4'><b>Name</b></th><th></th></tr>"); // Insert table header
		$.each(data, function(index, item) {
			//console.log(item.user_id + " - " + item.timeslot);
			var time = $("<td class='col-md-4'>" + item.timeslot + "</td>");
			var name = $("<td class='col-md-4'>" + item.username + "</td>");
			var accept_col = $("<td class='col-md-4'></td>");
			var accept_btn = $("<button class='btn btn-primary btn-block'>Accept</button>");
			accept_btn.click(function() {
				set_apt($("#top_pane").find("h3").attr("id"), item.user_id, item.timeslot, $(this));
				// Add some animations?
				load_business_main_pane($("#top_pane").find("h3").attr("id"));
			});
			accept_col.append(accept_btn);

			var row = $("<tr></tr>");
			row.append(time);
			row.append(name);
			row.append(accept_col);
			table.ref.append(row);
		})
		// Post processing
		element.empty(); // Clean out old data efore inserting new data.
		if (table.ref.find("tr").length == 1) {
			// No data found
			element.append("<p>No outstanding appointments requests found.</p>");
		} else {
			element.append(table.ref);
		}
	});
}

function logged_in(data) {
	// Hide login pane
	$("#login_pane").hide();
	// Show header pane
	load_header_pane(data);
	
	if (data.type == "business") {
		load_business_main_pane(data.id);
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
