function val_fecha(fecha) {

// console.log(fecha);
var fecha_array = fecha.split(" ");
// console.log(fecha_array);
var fecha_array_num = fecha_array[0].split("-");
// console.log(fecha_array_num);
var fecha_new = fecha_array_num[2] + " de ";

if (fecha_array_num[1] == 01){
  fecha_new += "Enero";
 }
else if (fecha_array_num[1] == 02){
   fecha_new += "Febrero";
  }
else if (fecha_array_num[1] == 03){
  fecha_new += "Marzo";
 }
else if (fecha_array_num[1] == 04){
   fecha_new += "Abril";
  }
else if (fecha_array_num[1] == 05){
   fecha_new += "Mayo";
  }
else if (fecha_array_num[1] == 06){
   fecha_new += "Junio";
  }
else if (fecha_array_num[1] == 07){
   fecha_new += "Julio";
  }
else if (fecha_array_num[1] == 08){
   fecha_new += "Agosto";
  }
else if (fecha_array_num[1] == 09){
   fecha_new += "Septiembre";
  }
else if (fecha_array_num[1] == 10){
   fecha_new += "Octubre";
  }
else if (fecha_array_num[1] == 11){
   fecha_new += "Noviembre";
  }
else if (fecha_array_num[1] == 12){
   fecha_new += "Diciembre";
  }
fecha_new += " de " + fecha_array_num[0];

return fecha_new
}
