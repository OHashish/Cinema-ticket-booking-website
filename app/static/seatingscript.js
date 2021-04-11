window.onload = function () {
    var contain = document.getElementById("container1");
    document.getElementById("hide").style.display = "none"

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
       if(!(e.currentTarget.classList.contains('selected')) && (document.getElementsByClassName("selected").length) <= quant-1){
   		   e.currentTarget.classList.add('selected');
       }
       else if((e.currentTarget.classList.contains('selected'))){
         e.currentTarget.classList.remove('selected');
       }

       quantity = (document.getElementsByClassName("selected").length);

       document.getElementById("book-btn").style.display = "inline-block"
       if (quantity<quant){
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

 });


};

function selectClass(){
  var select = (document.getElementsByClassName("selected"));
  var spaces=""
  var new_booked = []
  for(var i = 0; i < select.length; i++){
    spaces=select[i].innerHTML+","+spaces;
  }
  document.getElementsByName("something")[0].value=spaces;
}
