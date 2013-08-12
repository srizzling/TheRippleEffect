$(document).ready(function(){
        var university = new google.maps.LatLng(-41.29009971493793, 174.76815266036988)
        var mapOptions = {
          center: university,
          zoom: 7,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        var map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions)
        
        attachMarker(map, university);
        $("#lat").val(university.lat());
        $("#lng").val(university.lng());
});

function attachMarker(map, position){
        var clicked = false;
        var markerOpts = {
            map:map,
            draggable:true,
            position:position 
        };
        var marker = new google.maps.Marker(markerOpts);
        
        google.maps.event.addListener(marker, "mousedown", function(data){
            clicked = true;
        });
        google.maps.event.addListener(marker, "mouseup", function(data){
            clicked = false;
        });
        google.maps.event.addListener(map, "mousemove", function(data){
            if(clicked){
                console.log(data.latLng.lat);
                $("#lat").val(data.latLng.lat());
                $("#lng").val(data.latLng.lng());
            }
        });
}
