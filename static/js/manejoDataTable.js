var idioma= {
     "sProcessing":     "Procesando...",
     "sLengthMenu":     "Mostrar _MENU_ registros",
     "sZeroRecords":    "No se encontraron resultados",
     "sEmptyTable":     "Ningún dato disponible en esta tabla",
     "sInfo":           "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
     "sInfoEmpty":      "Mostrando registros del 0 al 0 de un total de 0 registros",
     "sInfoFiltered":   "(filtrado de un total de _MAX_ registros)",
     "sInfoPostFix":    "",
     "sSearch":         "Buscar:",
     "sUrl":            "",
     "sInfoThousands":  ",",
     "sLoadingRecords": "Cargando...",
     "oPaginate": {
         "sFirst":    "Primero",
         "sLast":     "Ultimo",
         "sNext":     "Siguiente",
         "sPrevious": "Anterior"
     },
     "oAria": {
         "sSortAscending":  ": Activar para ordenar la columna de manera ascendente",
         "sSortDescending": ": Activar para ordenar la columna de manera descendente"
     },
     "buttons": {
         "copyTitle": 'Información copiada',
         "copyKeys": 'Use your keyboard or menu to select the copy command',
         "copySuccess": {
             "_": '%d filas copiadas al portapapeles',
             "1": '1 fila copiada al portapapeles'
         },

         "pageLength": {
         "_": "Mostrar %d filas",
         "-1": "Mostrar Todo"
         }
     }
 };

function checkAll(bx) {
 var cbs = document.getElementsByTagName('input');
 for(var i=0; i < cbs.length; i++) {
   if(cbs[i].type == 'checkbox') {
     cbs[i].checked = bx.checked;
   }
 }
}
