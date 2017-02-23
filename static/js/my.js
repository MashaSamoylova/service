function l_ph() {
//  alert('lol')
  var xhr = new XMLHttpRequest();
  var input = this.elements.photo;
  var file = input.files[0];
//  alert(formData)
  xhr.open("POST", '/photo', true);
  xhr.send(file);
  alert(xhr.responseText);
}

function encode() {
  $("#log").val(btoa($("#log").val()));
  $("#pass").val(btoa($("#pass").val()));
}

function check() {
	var cookie = document.cookie;
	result_1 = cookie.match("user");
	var signature = document.getElementById("ability").value;
//	alert(signature);
	var realAbility = document.getElementById("rAbility").innerHTML;
	result_2 = signature == realAbility;
	if (!result_1 || !result_2) {
		alert("нет");
		return;
	}
	var xhr = new XMLHttpRequest();
	var body = "name=OK!!!!"
	xhr.open("POST", '/checkuser', false);
	xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
	xhr.send(body);
	alert(xhr.responseText);
//	location = '/';
//	setTimeout( 'location="/"', 0);
}

function send_msg() {
	var xhr = new XMLHttpRequest();
	msg = document.getElementById("letter").value;
	var body = "text=" + msg;
	xhr.open("POST", '/news', false);
	xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
	xhr.send(body);
	document.getElementById("letter").value = "";
}

function add_msg(xhr, counter) {
	var newMessage = JSON.parse(xhr.responseText);
	var span = document.getElementsByTagName('span')[0];
	for (var i=0; i<newMessage.length; i++, counter++) {
		letter = JSON.parse(newMessage[i]);
		var div_for_all = document.createElement('div');
		div_for_all.className = "col-md-offset-3 col-lg-offset-3 col-lg-6 col-md-6";
		div_for_all.style.cssText = "background: #FFFAFA; margin-top: 7px";
		div_for_all.innerHTML = '<p>' + counter.toString() + '</p>'
		span.insertBefore(div_for_all, span.firstChild);
		var div_for_img = document.createElement('div');
		div_for_img.className = "col-lg-2 col-md-2";
		div_for_img.style.cssText = "margin-top:10px; height:100px;";
		div_for_all.appendChild(div_for_img);
		var img = document.createElement('img');
		img.setAttribute('src', 'data:image/png;base64,' + letter['photo']);
		img.setAttribute('class', 'img-thumbnail');
		div_for_img.appendChild(img);
		var login = document.createElement('font');
		login.size = "5";
		login.innerHTML = letter['login'];
		div_for_all.appendChild(login);
		var paragraph = document.createElement('p');
		div_for_all.appendChild(paragraph);
		var text = document.createElement('font');
		text.size = "3";
		text.innerHTML = letter['text'];
		paragraph.appendChild(text);
	}
	return counter;
}

function sleep(ms) {
	  return new Promise(resolve => setTimeout(resolve, ms));

}

function get_message() {
	var counterOfMessages = document.getElementById("number").innerHTML;

	var timerId = setInterval(function() {
			var body = "lastMessage=" + counterOfMessages;
			var xhr = new XMLHttpRequest();
			xhr.open("POST", '/msg', true);
			xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
			xhr.send(body);
			xhr.onreadystatechange = function() {
				if (this.readyState != 4) return;
				if (this.status == 200) {
					res = String(this.responseText) === "no";
					if (res) {
						sleep(5000);
						return
					} //здесь нужен типо слип
					else{
						counterOfMessages = add_msg(this, counterOfMessages);
					}
				}
			}
	}, 5000);
}
