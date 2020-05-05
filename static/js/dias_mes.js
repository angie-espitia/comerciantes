function diasEnUnMes(mes, año) {
	mes = mes.toUpperCase();
	var meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"];
	return new Date(año, meses.indexOf(mes) + 1, 0).getDate();
}
