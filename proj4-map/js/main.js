var map = L.map('map', {
    layers: MQ.mapLayer(),
    center: [ 44.0519, -123.0867 ],
    zoom: 12
  });

var onMapClick = function(e) {
  // My gawd, I now understand all the scoping problems JS has. 
  // This code took so much effort to make elegant.

  var marker = L.marker();
  var popup = L.popup();

  var geocode = MQ.geocode().on('success', function(e) {
    var thisCode = geocode.describeLocation(e.result.best);
    // console.log(thisCode);
    popup.setContent(thisCode);
  });

  geocode.reverse(e.latlng);

  marker
    .setLatLng(e.latlng)
    .addTo(map)
    .bindPopup(popup);
}

map.on('click', onMapClick);

