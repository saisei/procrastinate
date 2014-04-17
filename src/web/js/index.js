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
		console.log(data);
	});
}

$( document ).ready(function() {
	$("#login").click(login);
});
