//***********************************************************************//
//                           Global Variables                            //
//***********************************************************************//

var map;
var styles; // map style options (roads, labels etc)
var townLabels = false; // display labels
var regions = [];
var riverLayer;
var lakeLayer;
var regionFillCol = '#FFFFFF';
var regionStrokeCol = '#2B547E';
var regionFillColShow = '#2B547E';
var regionStrokeColShow = '#2B547E';
var regionFillOpacity = 0.05;
var regionFillOpacityShow = 0.00;
var regionFillOpacityMouse = 0.32;
var regionStrokeWeight = 1;
var regionStrokeWeightShow = 3.1;
google.maps.visualRefresh = true;
   

//***********************************************************************//
//                              Functions                                //
//***********************************************************************//
function loadLayers() {
    riverLayer = new google.maps.FusionTablesLayer({
        map : map,
        heatmap : {
            enabled : false
        },
        query : {
            select : "col4",
            from : "1Cb9of1mmMn9YLrIFUlQe0wnOMZg-0zqQTRRJHT0",
            where : ""
        },
        options : {
            styleId : 2,
            templateId : 2
        }
    });

    lakeLayer = new google.maps.FusionTablesLayer({
        map : map,
        heatmap : {
            enabled : false
        },
        query : {
            select : "col10",
            from : "1_sDMfg9NEPd9WiwUe4OIxCSfO_A7Nr1p-TjTpUM",
            where : ""
        },
        options : {
            styleId : 2,
            templateId : 2

        }
    });
    riverLayer.setMap(null);
    lakeLayer.setMap(null);
}

//-----------------Display river overlay
function displayRivers() {
    if (riverLayer.getMap() == null && lakeLayer.getMap() == null) {
        riverLayer.setMap(map);
        lakeLayer.setMap(map);
    } else {
        riverLayer.setMap(null);
        lakeLayer.setMap(null);
    }
}


function createInfoWindow(fileName, title, description, date, tags, id) {
    var contentString = '<style> ' +
    '#content{word-wrap: break-word; max-width:400px;}' +
    '#image {height:300px; width:400px; }' +
    '#image img{max-width:100%; max-height:100%; margin:auto; display:block; -ms-interpolation-mode: bicubic}' +
    '</style>' +
    '<div id="content">' +
    '<div id="siteNotice">' +
    '</div>' +
    '<h2 id="firstHeading" class="firstHeading"> '+ title + '</h2>' +
    '<div id = "image">' +
    '<a href="' + fileName + '" target="_blank" ><img src="' + fileName +'" /></img></a>' +
    '</div>' +
    '<div id="bodyContent">' +
    '<p><b>Description:</b> '+ description +'</p>' +
    '<p><b>Uploaded:</b> '+ date +'</p>' +
    '<p><b>Tags:</b> ' + tags +'</p>' +
    '</div>' +
    '<button type="button" onclick="window.open('+"'"+'http://www.wainz.org.nz/image/'+id+''+"'"+');" >More Details</button>'+
    '</div>';
    info = new google.maps.InfoWindow({
        content: contentString
    });

return info;

}

//-----------------Create a marker
function createMarkers(location, iconName, info) {
    var bool = false;
    if(iconName == null){
        iconName = 'brown-drop.png';
    }

    for ( var i = 0; i < regions.length; i++) {
        if(bool == true)
            break;
        if(google.maps.geometry.poly.containsLocation(location,
            regions[i].polygon)) {
            var temp = new google.maps.Marker({
                position : location,
                map : this.map,
                icon : iconName,
            });

        temp.info = info;
        temp.setVisible(false);
        temp.setMap(map);
        regions[i].markers.push(temp);
        bool = true;
    }
}
}

//-----------------Show/hide markers in a region
function toggleRegionMarkers(region) {

    for ( var i = 0; i < region.markers.length; i++) {

        if (region.markers[i].getVisible() == true) {
            var temp = region.markers[i];
            temp.setVisible(false);
            temp.info.close();
            region.text.setMap(map);
            region.markers[i] = temp;
        } else { 
            region.text.setMap(null);
            temp = region.markers[i];
            temp.setVisible(true);
            region.markers[i] = temp;
        }
    }
}

//------------------Adds an event listener to a marker to open/close its infowindow
function addMarkerListener(marker) {
    google.maps.event.addListener(marker, 'click', function() {
        for ( var i = 0; i < regions.length; i++) {
            for ( var j = 0; j < regions[i].markers.length; j++) {
                if (regions[i].markers[j] != marker)
                regions[i].markers[j].info.close(); // close all other info windows
        }
    }
    if (marker.info.getMap() == null)
        marker.info.open(map, marker);
    else
        marker.info.close();
});
}

//-----------------Region object
function region(name, polygon) {
    this.polygon = polygon;
    this.name = name;
    this.markers = [];
    this.selected = false;
    this.center = null;
    this.text = null;
}

//-----------------Construct a polygon for a region
function constructPolygon(coordinates, name) {

    var r = new region(name, new google.maps.Polygon({
        paths : coordinates,
        strokeColor : regionStrokeCol,
        strokeOpacity : 0.8,
        strokeWeight : regionStrokeWeight,
        fillColor : regionFillCol,
        fillOpacity : regionFillOpacity
    }));
    var centerCoords = new google.maps.LatLngBounds();
    for (i = 0; i < coordinates.length; i++) {
        centerCoords.extend(coordinates[i]);
    }
    r.polygon.setMap(map);

    r.center = centerCoords.getCenter();
    regions.push(r);
}

//-----------------Add event handlers to a region
function AddEventHandlers(region) {
    google.maps.event.addListener(region.polygon, 'click', function() {
        regionSelector(region.polygon);
        toggleRegionMarkers(region);
    });

    google.maps.event.addListener(region.polygon, 'mouseover', function() {
        if (region.polygon.get('fillOpacity') == regionFillOpacity)
            region.polygon.setOptions({
                fillOpacity : regionFillOpacityMouse
            });
    });

    google.maps.event.addListener(region.polygon, 'mouseout', function() {
        if (region.polygon.get('fillOpacity') == regionFillOpacityMouse)
            region.polygon.setOptions({
                fillOpacity : regionFillOpacity
            });
    });
}

//-----------------Determine the selected region
function regionSelector(regionPoly) {
    if (regionPoly == null) { // multibox control
        DeselectRegions();
        var regionName = document.getElementById("region").value; // multibox value

        if (regionName == "All") {
            for ( var i = 0; i < regions.length; i++) {
                regions[i].text.setMap(null);
                regions[i].polygon.setOptions({
                    fillColor : regionFillColShow,
                    fillOpacity : regionFillOpacityShow,
                    strokeColor : regionStrokeColShow,
                    strokeWeight : regionStrokeWeightShow
                });
                for ( var j = 0; j < regions[i].markers.length; j++) {
                    regions[i].markers[j].setVisible(true);
                }
            }
        } else {
            for ( var i = 0; i < regions.length; i++) {
                if (regionName == regions[i].name) {
                    regions[i].text.setMap(null);
                    regions[i].polygon.setOptions({
                        fillColor : regionFillColShow,
                        fillOpacity : regionFillOpacityShow,
                        strokeColor : regionStrokeColShow,
                        strokeWeight : regionStrokeWeightShow
                    });
                    toggleRegionMarkers(regions[i]);
                    break;
                }
            }
        }
    } else { // user click control
        if (regionPoly.get('fillOpacity') == regionFillOpacityShow){
            regionPoly.setOptions({
                fillOpacity : regionFillOpacity,
                fillColor : regionFillCol,
                strokeColor : regionStrokeCol,
                strokeWeight : regionStrokeWeight
            });


            
        }
        else{

            regionPoly.setOptions({
                fillColor : regionFillColShow,
                fillOpacity : regionFillOpacityShow,
                strokeColor : regionStrokeColShow,
                strokeWeight : regionStrokeWeightShow
            });
        }
    }
}

//-----------------Deselect all regions
function DeselectRegions() {
    for ( var i = 0; i < regions.length; i++) {
        regions[i].text.setMap(map);
        regions[i].polygon.setOptions({
            fillColor : regionFillCol,
            fillOpacity : regionFillOpacity,
            strokeColor : regionStrokeCol,
            strokeWeight : regionStrokeWeight
        });
        regions[i].text.setMap(map);
        for ( var j = 0; j < regions[i].markers.length; j++) {
            regions[i].markers[j].setVisible(false);
            regions[i].markers[j].info.close();
        }
    }
}


    

//***********************************************************************//
//                            Create the Map                             //
//***********************************************************************//
function initialize() {

    var mapCanvas = document.getElementById('map_canvas');
    var mapOptions = {
        center : new google.maps.LatLng(-41, 172),
        zoom : 6,
        mapTypeId : google.maps.MapTypeId.TERRAIN, //ROADMAP SATELLITE
        panControl : false,
        streetViewControl : false,
        scaleControl : true,
        mapTypeControlOptions: {
            style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
        },
        disableDoubleClickZoom : true,
        zoomControlOptions : {
            style : google.maps.ZoomControlStyle.DEFAULT,
            position : google.maps.ControlPosition.RIGHT_CENTER
        }
    };
    map = new google.maps.Map(mapCanvas, mapOptions);

    //-----------------Limit the zoom level
    google.maps.event.addListener(map, 'zoom_changed', function() {
        if (map.getZoom() < 6){
            map.setZoom(6);
        }
    });

    //-----------------Set the map style
    styles = [ {
        featureType : "road", // turn off roads
        stylers : [ {
            visibility : "off"
        } ]
    }, {
        featureType : "poi", // hide 'points of interest'
        stylers : [ {
            visibility : "off"
        } ]
    }, {
        featureType : "transit",
        stylers : [ {
            visibility : "off"
        } ]
    }, {
        featureType : "all", // hide all labels
        elementType : "labels",
        stylers : [ {
            visibility : "off"
        } ]
    }, {
        featureType : "water", // water colour + labels
        elementType : "geometry.fill",
        stylers : [ {
            color : "#99b3cc"
        } //2B547E 3090C7
        ]
    }, {
        featureType : "water",
        elementType : "labels.text.stroke",
        stylers : [ {
            visibility : "on"
        }, {
            color : "#FF0000"
        }, ]
    }, {
        featureType : "water",
        elementType : "labels.text.fill",
        stylers : [ {
            visibility : "on"
        }, {
            color : "#FFFFFF"
        }, {
            weight : 25
        } ]
    }, {
        featureType : "landscape", // country colour
        elementType : "geometry.fill",
        stylers : [ {
            color : "#c7d9a7"
        }, //#D1D0CE
        ]
    }, {
        featureType : "administrative.province", // region borders
        elementType : "all",
        stylers : [ {
            visibility : "off"
        }, ]
    } ];
    map.setOptions({
        styles : styles
    });

    google.maps.event.addListener(map, 'maptypeid_changed',
        function() {
            if (map.getMapTypeId() == 'satellite'
             || map.getMapTypeId() == 'hybrid') {
             regionStrokeCol = '#FFFFFF';
         regionStrokeColShow = '#FFFFFF';
     } else if (map.getMapTypeId() == 'terrain') {
        regionStrokeCol = '#2B547E';
        regionStrokeColShow = '#2B547E';
    } else if (map.getMapTypeId() == 'roadmap') {
        regionStrokeCol = '#2B547E';
        regionStrokeColShow = '#2B547E';
    }
    DeselectRegions();
});

    //-----------------Construct regional overlays
    constructPolygon(loadNorthland(), "Northland");
    constructPolygon(loadAuckland(), "Auckland");
    constructPolygon(loadWaikato(), "Waikato");
    constructPolygon(loadWestcoast(), "West Coast");
    constructPolygon(loadBayofplenty(), "Bay of Plenty");
    constructPolygon(loadCanterbury(), "Canterbury");
    constructPolygon(loadGisborne(), "Gisborne");
    constructPolygon(loadOtago(), "Otago");
    constructPolygon(loadSouthland(), "Southland");
    constructPolygon(loadHawkesbay(), "Hawke's Bay");
    constructPolygon(loadTasman(), "Tasman");
    constructPolygon(loadTaranaki(), "Taranaki");
    constructPolygon(loadManawatu(), "Manawatu-Wanganui");
    constructPolygon(loadNelson(), "Nelson");
    constructPolygon(loadWellington(), "Wellington");   
    constructPolygon(loadMarlborough(), "Marlborough");


    for ( var i = 0; i < regions.length; i++)
        AddEventHandlers(regions[i]);


    //Hard coded temporary points for proof of concept
    var points = [{'extension': 'jpg', 'image_name': 'Cows and a pig in the Kaeo River', 'lat': '-35.0898333333', 'path': '//www.wainz.org.nz/static/uploaded-images/243695398329515817226931691155125491443', 'lng': '173.7676666667', 'id': 74}, 
    {'extension': 'jpg', 'image_name': 'North Canterbury beef stock in stream', 'lat': '-42.6307673469', 'path': '//www.wainz.org.nz/static/uploaded-images/89914717573047748667166252363738837018', 'lng': '173.1396888950', 'id': 31}, 
    {'extension': 'jpg', 'image_name': 'Ihumatao - Oruarangi creek', 'lat': '-36.9798380399', 'path': '//www.wainz.org.nz/static/uploaded-images/40077846748125228723856284165115698322', 'lng': '174.7628266609', 'id': 75}, 
    {'extension': 'jpg', 'image_name': 'Stock in river', 'lat': '-36.6313454500', 'path': '//www.wainz.org.nz/static/uploaded-images/267333552515848401917699247648915644642', 'lng': '175.4745340347', 'id': 65}, 
    {'extension': 'jpg', 'image_name': 'Cows in river', 'lat': '-41.2834905869', 'path': '//www.wainz.org.nz/static/uploaded-images/4234521036228318747925117750426449282', 'lng': '175.6608375907', 'id': 66}, 
    {'extension': 'jpg', 'image_name': 'Just north of Carterton', 'lat': '-41.0221930018', 'path': '//www.wainz.org.nz/static/uploaded-images/85374843667129068625713784148686059742', 'lng': '175.5607570540', 'id': 76}, 
    {'extension': 'jpg', 'image_name': 'Mangaokewa, Te Kuiti', 'lat': '-38.3341631737', 'path': '//www.wainz.org.nz/static/uploaded-images/198323447572416469987830335439486251667', 'lng': '175.1677943993', 'id': 69}, 
    {'extension': 'JPG', 'image_name': 'Manawatu River', 'lat': '-41.2900997149', 'path': '//www.wainz.org.nz/static/uploaded-images/245743661757911788429686004627085415186', 'lng': '174.7681526604', 'id': 77}, 
    {'extension': 'jpg', 'image_name': 'Cherry island taupo', 'lat': '-38.6773182435', 'path': '//www.wainz.org.nz/static/uploaded-images/279789384298890445560306479313046407886', 'lng': '176.0830097757', 'id': 71}, 
    {'extension': 'jpg', 'image_name': 'Otahu river whangamata', 'lat': '-37.2353333333', 'path': '//www.wainz.org.nz/static/uploaded-images/309131387348949667208182903313572842483', 'lng': '175.8441666667', 'id': 72}, 
    {'extension': 'jpg', 'image_name': 'Beef cows in the Kaeo river Northland', 'lat': '-35.0953389418', 'path': '//www.wainz.org.nz/static/uploaded-images/241367489107703108199158756949244494487', 'lng': '173.7731507560', 'id': 73}, 
    {'extension': 'jpg', 'image_name': 'feedlot', 'lat': '-39.9602803543', 'path': '//www.wainz.org.nz/static/uploaded-images/312318377253163054147030580165596946856', 'lng': '176.6546630859', 'id': 104}, 
    {'extension': 'jpg', 'image_name': 'Kakapotahi river oil spill', 'lat': '-43.0071286908', 'path': '//www.wainz.org.nz/static/uploaded-images/86459809820991683833063977168781532255', 'lng': '170.7435547964', 'id': 101}, 
    {'extension': 'JPG', 'image_name': 'Kawhatau River', 'lat': '-41.2900997149', 'path': '//www.wainz.org.nz/static/uploaded-images/309229793600700305913124669277978193640', 'lng': '174.7681526604', 'id': 100}, 
    {'extension': 'jpg', 'image_name': 'Clean river above farms runoff', 'lat': '-37.2660000000', 'path': '//www.wainz.org.nz/static/uploaded-images/87522579744651000013162890152487273256', 'lng': '175.8345000000', 'id': 85}, 
    {'extension': 'JPG', 'image_name': 'SH53', 'lat': '-41.2900997149', 'path': '//www.wainz.org.nz/static/uploaded-images/49829753665157234762976905096478417552', 'lng': '174.7681526604', 'id': 87}, 
    {'extension': 'JPG', 'image_name': 'Tuakau, North Waikato', 'lat': '-41.2900997149', 'path': '//www.wainz.org.nz/static/uploaded-images/163257200272820323333514426063617433536', 'lng': '174.7681526604', 'id': 117}, 
    {'extension': 'jpg', 'image_name': 'feedlot on river', 'lat': '-39.9434364620', 'path': '//www.wainz.org.nz/static/uploaded-images/12134325451602530810715733871881281727', 'lng': '176.6546630859', 'id': 105}, 
    {'extension': 'jpg', 'image_name': 'OLD Waipawa river bed', 'lat': '-39.9771200984', 'path': '//www.wainz.org.nz/static/uploaded-images/18397363273428760096505715131402403585', 'lng': '176.5118408203', 'id': 106}, 
    {'extension': 'jpg', 'image_name': '', 'lat': '-41.3228252727', 'path': '//www.wainz.org.nz/static/uploaded-images/242468383331370402552151624510231644065', 'lng': '173.1582760348', 'id': 108}, 
    {'extension': 'jpg', 'image_name': 'Whau Estuary Pollution', 'lat': '-36.8631414330', 'path': '//www.wainz.org.nz/static/uploaded-images/74298425246354173290188832744210528168', 'lng': '174.6560096741', 'id': 120}, 
    {'extension': 'jpg', 'image_name': 'Aratitia rapids', 'lat': '-38.6159379939', 'path': '//www.wainz.org.nz/static/uploaded-images/79616475897059200773379118519225608853', 'lng': '176.1414284965', 'id': 119}, 
    {'extension': 'jpg', 'image_name': 'Wainui Stream, Paekakariki', 'lat': '-40.9766171339', 'path': '//www.wainz.org.nz/static/uploaded-images/204609434489357963808645843905837819961', 'lng': '174.9658466019', 'id': 121}, 
    {'extension': 'jpg', 'image_name': 'Foam Pollution', 'lat': '-36.9014157136', 'path': '//www.wainz.org.nz/static/uploaded-images/285707902342278628524736369292301415102', 'lng': '174.6849185228', 'id': 122}, 
    {'extension': 'jpg', 'image_name': 'Avon River Christchurch ', 'lat': '-43.5088333333', 'path': '//www.wainz.org.nz/static/uploaded-images/216635625063130034243286474750037167002', 'lng': '172.7206666667', 'id': 141}, 
    {'extension': 'jpg', 'image_name': 'Urban Stormwater pollution', 'lat': '-36.7691170095', 'path': '//www.wainz.org.nz/static/uploaded-images/293044740516495894773979580551735086415', 'lng': '174.7408054897', 'id': 144}, 
    {'extension': 'jpg', 'image_name': 'Opihi River', 'lat': '-44.1697692409', 'path': '//www.wainz.org.nz/static/uploaded-images/305370187809105796995878458073365465441', 'lng': '170.9713518620', 'id': 147}, 
    {'extension': 'jpg', 'image_name': 'Whakamaru2013-2', 'lat': '-38.4108272709', 'path': '//www.wainz.org.nz/static/uploaded-images/257707619820531229678247493517074568808', 'lng': '175.8097457886', 'id': 125}]

    //Import data from API stored as JSON using jQuery (AJAX) 
    //TO BE COMPLETED
    // $.getJSON('www.wainz.org.nz/api/export', function(data) {
    //     $.each(data function(point){
    //         points.push(point); // Something like this
    //     });
       
    // });

    var defaultInfo = createInfoWindow("river1.jpg", "A River",
        "This is a river that is good", "10/10/10", "River, No Cows, Clean", 0);

    for ( var i = 0; i < points.length; i++){
        createMarkers(
            new google.maps.LatLng(points[i].lat, points[i].lng),
            null,
            createInfoWindow("http:" + points[i].path + "."
                + points[i].extension + "", points[i].image_name,
                "Description not available", "??/??/??", "Tags not available", points[i].id));
    }

    //Set labels
    for(var i=0; i < regions.length; i++){
     if(regions[i].name == "Wellington"){
         var mapLabel = {
         text: regions[i].markers.length-3,
         position: regions[i].center,
         map: map,
         fontSize: 20,
         fontColor: 'white',
         strokeColor: regionStrokeCol,
         fillOpacity: 1,
         strokeOpacity: 1,
         };
     }
     else {

         var mapLabel = {
             text: regions[i].markers.length,
             position: regions[i].center,
             map: map,
             fontColor: 'white',
             strokeColor: regionStrokeCol,
             fontSize: 20,
         };
     }

     var label = new MapLabel(mapLabel)
     regions[i].text = label;
    }




    //-----------------Add event handlers       
    for ( var i = 0; i < regions.length; i++) {
        for ( var j = 0; j < regions[i].markers.length; j++) {
            addMarkerListener(regions[i].markers[j]);
        }
    }
    //-----------------Load the river + lake overlay
    loadLayers();

}
google.maps.event.addDomListener(window, 'load', initialize);