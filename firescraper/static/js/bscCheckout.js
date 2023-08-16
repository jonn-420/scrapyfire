async function ans(){
	//const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
	//console.log(csrftoken);
	var details='pending...';
	await fetch('/gStart', {
		method :'GET',
	//	headers: {'X-CSRFToken': csrftoken},
      //  mode:'same-origin',
	}).then(function(response){
		details =response.json();			
		location.href='#keytext';
		return details;
	});
	document.getElementById('keytext').innerHTML = details.api_key;
	return details;
}
function func(){
	ans().then((data)=>{
		document.getElementById('keytext').innerHTML = data.api_key;
	});
}