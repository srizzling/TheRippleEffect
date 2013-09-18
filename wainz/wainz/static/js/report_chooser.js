var map
var submission_ids = []
$(document).ready(function(){
        var mapOptions = {
          center: new google.maps.LatLng(-41.29009971493793, 174.76815266036988),
          zoom: 7,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions)
        for(var i in points){
           addMarker(i) 
        }
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
        if(!~submission_ids.indexOf(id)){
            addToSelected(image_path, image_extension, id);
            submission_ids.push(id)
            replaceSubmissionIds();
        }
    });
}

function addToSelected(image_path, image_extension, id){
    $("<li class='span3' id='thumb-"+id+"' style='text-align:center'>"+
      " <a href='#' class='thumbnail'>"+
      "  <img src='/static/images/"+image_path+"."+image_extension+"' />"+
      " </a>"+
      "</li>").appendTo($("#thumbs"));
    $("#thumb-"+id).click(function(){
        var idx = submission_ids.indexOf(id);
        if(idx != -1) submission_ids.splice(idx, 1);
        $("#thumb-"+id).hide(function(){$(this).remove();});
        replaceSubmissionIds();
    });
}

function replaceSubmissionIds(){
    $("#sub_ids").val("");
    for(var idx in submission_ids){
        $("#sub_ids").val($("#sub_ids").val()+","+submission_ids[idx]);
    }
}
