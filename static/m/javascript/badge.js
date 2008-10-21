function swapbutton(buttonurl) {
  e = document.getElementById('network-badge');
  var codetocopy = e.value;
  var newcodetocopy = codetocopy.replace(/src=".*?"/, 'src="'+buttonurl+'"');
  e.value = newcodetocopy;  
}
