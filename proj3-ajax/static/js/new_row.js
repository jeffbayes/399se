function addRow() {
	var newRow = $(
		'<div class="row">' +
			'<div class="col-md-2">' +
				'<input type="text" class="form-control" name="distance" placeholder="Distance"/>' +
			'</div>' + 
			'<div class="col-md-4">' +
				'<input type="text" class="form-control"name="location" placeholder="location" />' +
			'</div>' +
			'<div class="col-md-6">' +
				'<span class="times form-control">...</span>' +
			'</div>' + 
		'</div>');

	$('form.brevet-calc').append(newRow);
	$('input[name="distance"]').on("change", function(){
      changeFunction( $(this) );
    });
}

function removeRow() {
	$('form.brevet-calc div.row:last').remove();
}

function updateAll() {
	$('input[name="distance"]').each(function(){
		changeFunction( $(this) );
	});
}