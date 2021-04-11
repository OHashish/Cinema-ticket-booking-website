function onMovieChange(s){
	console.log(s.value);
	console.log(movieids.length);
	var screenings = document.getElementById("show_no");
	var v = "";

	for(var i = 0; i<movietitles.length; i++){
		console.log(movieids[i]);

 		if(s.value.toString()==movietitles[i]){
			console.log(s.value);

			for(var a = 0; a<screenids.length; a++){
				console.log(screenids[a]);
				if(screenids[a]==movieids[i]){
					console.log(movieids[i]);
					console.log(screentimes[a]);
					v+= "<option>"+screentimes[a]+"</option>";
				}				
			}
		}
	}
	console.log(v);
	screenings.innerHTML = v;
}
