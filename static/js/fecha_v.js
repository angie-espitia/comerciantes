function val_fecha(fecha) {

console.log(fecha);
var fecha_array = fecha.split(" ");
console.log(fecha_array);
var fecha_array_num = fecha_array[0].split("-");
console.log(fecha_array_num);
var fecha_new = fecha_array_num[2] + " de ";

if (fecha_array_num[1] == 08){
  fecha_new += "Agosto";
 }

fecha_new += " de " + fecha_array_num[0];

return fecha_new
}
