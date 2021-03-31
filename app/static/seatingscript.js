window.onload = function () {
    var contain = document.getElementById("container1");

    var bookedSeats = [5,14,16]

   function makeRows(rows, cols) {
     contain.style.setProperty('--grid-rows', rows);
     contain.style.setProperty('--grid-cols', cols);
     for (c = 0; c < (rows * cols); c++) {
       let cell = document.createElement("div");
       cell.innerText = (c + 1);
       cell.id = "seat" + c;
       cell.num = c;
       contain.appendChild(cell).className = "seat";
     };
   };

   makeRows(10, 5);

   $('.seat').click((e) => {
   	if(!(e.currentTarget.classList.contains('booked'))) {

   		e.currentTarget.classList.toggle('selected');

       quantity = (document.getElementsByClassName("selected").length);

       document.getElementById("quantity").innerHTML = quantity + " Ticket(s)"
       document.getElementById("book-btn").style.display = "inline-block"
       if (quantity==0){
       	document.getElementById("quantity").innerHTML = "Select your seats!"
       	document.getElementById("book-btn").style.display = "none"
       }
     }
   });

   for(var i in bookedSeats){
   	booked = (document.getElementById("seat" + bookedSeats[i]));
     booked.className = "seat booked"
   }

   $('#book-btn').click((e) => {


     var all = $(".selected").map(function() {
       return this.num;
   }).get();
   console.log(all);

   })
   console.log("Hello World")

};
