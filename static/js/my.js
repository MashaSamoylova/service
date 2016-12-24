function l_ph(){
//  alert('lol')
  var xhr = new XMLHttpRequest();
  var input = this.elements.photo;
  var file = input.files[0];
//  alert(formData)
  xhr.open("POST", '/photo', true);
  xhr.send(file);
  alert(xhr.responseText);
}

function encode(){
  $("#log").val(btoa($("#log").val()));
  $("#pass").val(btoa($("#pass").val()));
}
