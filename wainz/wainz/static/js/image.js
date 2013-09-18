$(document).ready(function(){
      $(".ttip").tooltip()      
      var center = new google.maps.LatLng(lat, lng);
      var mapOptions = {
           center: center,
           zoom: 7,
           zoomControl:false,
           streetViewControl:false,
           panControl:false, 
           mapTypeId: google.maps.MapTypeId.ROADMAP
          };         
      map = new google.maps.Map(document.getElementById("maps"), mapOptions)
      var markerOpts = {map:map, position: center}
      var marker = new google.maps.Marker(markerOpts);         
      var firstTimeRound = true;
      google.maps.event.addListener(map, 'tilesloaded', function(){
         if(firstTimeRound){
             firstTimeRound = !firstTimeRound;
             $("#maps").css({"display":"none"});
             $("#map_container").append($("#maps"));
             $("#loc").toggle(function(e){          
              $("#maps").show({"effect":"explode"}, function(){google.maps.event.trigger(map, 'resize'); map.setCenter(center)});    
                  $("#img").hide({"effect":"explode"});
              }, function(e){
                  $("#maps").hide({"effect":"explode"}, function(){google.maps.event.trigger(map, 'resize'); map.setCenter(center)});
                  $("#img").show({"effect":"blind"});
             });
         };
      });     
      
      
      $("#submit").click(function(e){
         //stop the form from submitting like usual
         e.preventDefault();
         //and instead populate a post call
         if($("#comment").val() == '') {
            $("#comment-empty").show('blind');
            return;
         }
         
         var data = {                
                "csrfmiddlewaretoken":$("#csrf").find('input').val(),
         };
         data['comment'] = $("#comment").val();
         data['id'] = img_id;
         data['uid'] = current_uid;


         if(!data['uid'] || data['uid'] == "None"){
             $("#comment-auth").show('blind');
             return;
         }
         $.post("/add_comment/", data, function(data){
           var placeholder_id = Math.random();
           var placeholder = $("<div class='span12 well comment' style='display:none' id='placeholder-"+placeholder_id+"'>"+
                               "<span>"+$("#comment").val()+"</span> <br />"+
                               "<span class='comment time'>"+user_name+" | at: "+(new Date()).toString()+"</span>"+
                               "</div>").prependTo($("#comment_container")).show({effect:'explode'});
           $("#comment").val('');
           if(!$("comment-empty").hasClass('hide')) $("#comment-empty").hide('blind');
         }).error(function() {
               $("#comment-error").show('scale');
           }); 
      });
      $("#add_tag").click(function(e){
          e.preventDefault()
          $("<div class='modal hide fade'>\
             <div class='modal-header'>\
             <button type='button' class='close' data-dismiss='modal' aria-hidden='true'>&times;</button>\
             <h2>Add a tag to this image</h2></div>\
             <div class='modal-body'>Attach an existing tag, or add your own: <input type='text' id='tag_text' style='width:100%' autocomplete='off'></input></div>\
             <div class='modal-footer'><button class='btn btn-success' id='add_tag_submit'>Submit</button></div>\
             </div>")
          .modal().on('shown', function(){
              $("#tag_text").typeahead({source:typeAheadSource});
              $("#add_tag_submit").click(function(e){
                  var tag_text = $("#tag_text").val();
                  if(tag_text == ''){
                      if(!$("#empty_tag").length)
                      $("<div id='empty_tag' class='alert alert-error hide'>Cannot add an empty tag!</div>").appendTo($(".modal-body")).show('blind');
                  }else if(tag_text.length > 30){
                      if(!$("#lengthy_tag").length)
                      $("<div id='lengthy_tag' class='alert alert-error hide'>Tags must be less than 30 characters</div>").appendTo($(".modal-body")).show('blind');
                  }else if("{{current_user_id}}" == 'None'){
                      if(!$("#auth_tag").length)
                      $("<div id='auth_tag' class='alert alert-error hide'>You must be logged in to add a tag</div>").appendTo($(".modal-body")).show("blind");
                  }else{
                      var post = {                
                          "csrfmiddlewaretoken":$("#csrf").find('input').val(),
                      };
                      if(!current_uid){
                          $("<div id='auth_tag' class='alert alert-error hide'>You must be logged in to add a tag</div>").appendTo($(".modal-body")).show("blind");
                          return;
                      }

                      post['tag'] = tag_text;
                      post['id'] = img_id;
                      $.post("/add_tag/", post, function(data){
                          if(data['added']){
                            $("#tags").append($("<span class='tag'>| "+tag_text+" </span>"));
                            $("<div id='success' class='alert alert-success hide'>Tag added</div>").appendTo($(".modal-body")).show('blind');
                          }
                          setTimeout(function(){$('.modal').modal('hide'); $('.modal').remove();}, 2000);
                      }).error(function(data){
                          $("<div id='failed_post' class='alert alert-error hide'>Something broke : (, maybe refresh and try again</di>").appendTo($(".modal-body")).show('blind');
                          setTimeout(function(){$('.modal').modal('hide'); $('.modal').remove();}, 2000);
                      });
                  }
              });
          });
      });
  });
