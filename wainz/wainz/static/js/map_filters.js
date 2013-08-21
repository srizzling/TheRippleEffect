
geofilters = []
tags = []

$(document).ready(function () {
        var date = new Date();
        $("#from").val(date.getDate()+"/"+(date.getMonth()+1)+"/"+date.getFullYear());
        $("#to").val(date.getDate()+"/"+(date.getMonth()+1)+"/"+date.getFullYear());
        //Create the datepicker objects,
        //and make the pop-ups disappear
        //as soon as you click one
        $(".datepicker").datepicker()
                        .on('changeDate', function () {
                            $(this).datepicker('hide');
                        });
        $("#add_tag_filter").click(function(e){
            e.preventDefault();
            var tag_text = $("#add_tag_text").val();
            if(tag_text != "" && !~tags.indexOf(tag_text)){
                $("#tag_filter").prop("checked", true);
                tags.push(tag_text);
                $("<div class='alert alert-success hide'>\
                   <button type='button' class='close' data-dismiss='alert'>×</button><span class='tag'>"+tag_text+"</span></div>")
                .appendTo($("#tag-container"))
                .show('blind');
            }
        });
        $("#tag-container").on('click', 'button.close',  function(e){
            var tag_text = $(this).siblings().text();
            for(var idx in tags){
                if(tags[idx] == tag_text){
                    tags.splice(idx, 1); break;
                }
            }
            if(tags.length == 0) $("#tag_filter").prop("checked", false);
        });
        $("#add_tag_text").typeahead({"source":tagTypeaheadSource});
        //Adding a geofilter pushes a helper function onto
        //the list, which we can use to detect how many, 
        //and the positions, of geo filters in place
        $("#add_geo_filter").click(function(){
            console.log(geofilters)
            var university = new google.maps.LatLng(-41.29009971493793, 174.76815266036988)
            $("#geo_filter").prop('checked', true)
            appendFields(geofilters.length+1);
            geofilters.push(attachGeoFilter(university, geofilters.length+1));
        });
        //Make sure you cannot exclude location filter in yr search while
        //there are still geo filters
        $("#geo_filter").click(function(e){
            if(!$(this).prop('checked') && geofilters.length > 0){
                e.preventDefault();
            }
        }); 
        //Altering one of the date time choosers will automatically turn
        //the corresponding check box on
        $('.datepicker').on('changeDate', function(){
            $("#date_filter").prop('checked', 'checked');
        });
        //submit the search form to the post end end point.
        //we have to go through a bit more work to create 
        //the request dictionary manually as we are not posting
        //the form in the default manner (i.e. subselections
        //apply)
         $("#search_submit").click(function (){
            var data = {                
                "csrfmiddlewaretoken":$("#csrf").find('input').val(),
            };
            data["date_filter"] = $("#date_filter").prop('checked');
            data["geo_filter"] = $("#geo_filter").prop('checked');
            data["tag_filter"] = $("#tag_filter").prop('checked');
            if($("#date_filter").prop('checked')){
                data["from"] = $("#from").val();
                data["to"]   = $("#to").val();
            }
            if($("#geo_filter").prop('checked')){
                data["filters"] = geofilters.length;
                for(var idx in geofilters){
                    var g = geofilters[idx];
                                  
                    data["filter_"+idx+"_lat"] = g.lat();
                    data["filter_"+idx+"_lng"] = g.lng();
                    data["filter_"+idx+"_rad"] = g.rad();  
                    
                }
            }
            if($("#tag_filter").prop('checked')){
                data['conjunctive'] = ($("#tag_type").val() == "all");
                var tag_data =  ""
                $(".tag").each(function(){ tag_data += $(this).text()+','; });
                data["tags"] = tag_data
            }
            $.post("/search/", data, function(data){
                //remove the old markers from the map
                for(var idx in markers){
                    markers[idx].setMap(null)
                }
                //remove their pointers
                markers = []
                //set the raw data
                points = data.points
                for(var idx in data.points){
                    addMarker(idx)
                }
            });
        });
    });

//Attaches a geofilter object (a manipulable circle)
//to the map, and returns an object representing it
//the can be queried for the lat, lng and radius
function attachGeoFilter(position, id){

    var circleOpts = {
        center:position,
        fillColor:"#77F",
        fillOpacity:0.6,
        map:map,
        radius:50000,
        strokeWeight:0,
        editable:true,
    }
    var circle = new google.maps.Circle(circleOpts);
    $("#lat"+id).val(position.lat());
    $("#lng"+id).val(position.lng());
    $("#radius"+id).val(50000);
    google.maps.event.addListener(circle, 'center_changed', function(){
        $("#lat"+id).val(circle.getCenter().lat());
        $("#lng"+id).val(circle.getCenter().lng());
    });
    google.maps.event.addListener(circle, 'radius_changed', function(){
        $("#radius"+id).val(circle.getRadius());
    });
    var GeoFilter = {
        id : id,
        del: function del() { return circle.setMap(null); },
        lat: function lat() { return circle.getCenter().lat(); },
        lng: function lng() { return circle.getCenter().lng(); },
        rad: function rad() { return circle.getRadius(); },
        setSelected: function setSelected(bool) { bool ? circle.set('fillColor', '#F77') : circle.set('fillColor', '#77f'); }
    }
    return GeoFilter;
}
//Appends the necessary form fields for each new location filter that is applied
function appendFields(field_id){
    var container_div = $("<div id='set_"+field_id+"'>")
    var label  = $("<h4>Filter "+field_id+"</h4><a href='#'><i id='icon-"+field_id+"' class='icon-question-sign'></i></a><span style='color:#333'>Highlight this filter</span>");
    var delete_button = $("<button id='delete_"+field_id+"' class='delete btn btn-danger pull-right'>Delete</button>");
    var lat = $("<label>Latitude</label><input type='text' id='lat"+field_id+"' name='lat"+field_id+"' readonly='readonly' />");
    var lng = $("<label>Longitude</label><input type='text' id='lng"+field_id+"' name='lng"+field_id+"' readonly='readonly' />");
    var radius = $("<label>Radius</label><input type='text' id='radius"+field_id+"' name='radius"+field_id+"' readonly='readonly' />");
    var filter_container = $("#geofilters");
    filter_container.append(container_div);
    container_div.append(label)
                 .append(delete_button)
                 .append(lat)
                 .append(lng)
                 .append(radius);
    //Add listeners to the newly created button elements

    $("#delete_"+field_id).click(function(e){
        var geofilter_idx = getGeoFilterIdForFieldId(field_id);
        $("#set_"+field_id).remove()
	    geofilters[geofilter_idx].del();
	    geofilters.splice(geofilter_idx, 1);                
        if(geofilters.length == 0) $("#geo_filter").prop("checked", false);
    });
    $('#icon-'+field_id).toggle(
      function(e){
        var geofilter_idx = getGeoFilterIdForFieldId(field_id);
        /*$("#set_"+field_id).css({"background-color":"#FDD"})
                           .siblings()
                           .css({"background-color":"#f5f5f5"});*/
        for(var idx in geofilters){
             geofilters[idx].setSelected(idx == geofilter_idx);
	    }
      },
      function(e){
        var geofilter_idx = getGeoFilterIdForFieldId(field_id);
        $("#set_"+field_id).css({"background-color":"F5F5F5"});
        geofilters[geofilter_idx].setSelected(false);
      }
    );
}

function getGeoFilterIdForFieldId(field_id){
    for(var idx in geofilters){
        if(geofilters[idx].id == field_id){
	    return idx;
	}
    }
}







