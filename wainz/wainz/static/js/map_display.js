/*references server side variables: 'points'*/
var map
$(document).ready(function(){
        var mapOptions = {
          center: new google.maps.LatLng(-41.29009971493793, 174.76815266036988),
          zoom: 6,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions)
        for(var i in points){
           addMarker(i) 
        }
        google.maps.event.addListener(map, "click", function(l){console.log("Xa: "+l.latLng.lat()+", Ya: "+l.latLng.lng());});
});

function addMarker(i){
    var ltln = new google.maps.LatLng(points[i].lat, points[i].lng);
    var markerOpts = {position:ltln, map:map};
    var marker = new google.maps.Marker(markerOpts);
    addImagePopOverListener(marker, points[i].path, points[i].image_name, points[i].extension, points[i].id);
    markers.push(marker)
}



function addImagePopOverListener(marker, image_path, image_name, image_extension, id){
    google.maps.event.addListener(marker, 'click', function(data){
        $('<div id="image-popup" class="modal hide fade"> \
             <div class="modal-header">\
               <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>\
               <h3>'+image_name+'</h3>\
             </div>\
             <div class="modal-body">\
               <div id="modal-image" class="centered">\
               <img src="'+image_path+'.'+image_extension+'" />'+'\
               </div>\
             </div>\
             <div class="modal-footer">\
               <a href="/image/'+id+'" class="btn btn-info">View Detail</a>\
               <a href="#" class="btn" data-dismiss="modal">Close</a>\
             </div>\
           </div>').modal();
    });
}


