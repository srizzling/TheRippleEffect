from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import wainz.models
from django.contrib.auth.models import User
from datetime import datetime
from django.core.urlresolvers import reverse
import search_utils
from django.conf import settings
from django.utils import timezone

import time
import json
import os
import base64
import random
import tag_utils
import PIL.Image

@csrf_exempt
def image(request):
    """
    A RESTful image resource endpoint.
      * GET: currently will result in error status 405, request method not allowed
      * PUT: currently will result in error status 405, request method not allowed
      * POST: stores an image to the data base and returns success, or returns one of:
             * 415 Unsupported media; image filetype cannot be interpreted as base64 json
             * 400 Bad request: request syntax did not match API grammar
      * PATCH: returns 405, method not allowed
      * DELETE: returns 405, method not allowed
      * CONNECT: returns 405, method not allowed
      * TRACE: as per standard, returns the request as seen by the server
      * OPTIONS: as per standard, returns possible uri requests resulting from a 
                 successful call to this uri
    """
    #print 'image request found'
    #Request types we are not going to support through an id-less request
    #if a user wants to GET images, they should instead OPTIONS a /user resource
    #and follow the supplied uris
    if request.method == 'GET' or request.method == 'PUT' or request.method == 'PATCH' or request.method == 'DELETE' or request.method == 'CONNECT':
        respDict = {}
        respDict["status"] = "ERROR"
        respDict["error_message"] = "Incorrect request method (expected POST)"
        respDict["url"] = request.build_absolute_uri()
        responseData = json.dumps(respDict)
        response = HttpResponse(responseData, "application/json", 405)
        return response

    if request.method == 'OPTIONS':
        respDict = {}
        respDict["status"] = "ERROR"
        respDict["error_message"] = "Request verb not implemented"
        respDict["url"] = request.build_absolute_uri()
        responseData = json.dumps(respDict)
        response = HttpResponse(responseData, "application/json", 501)
        return response

    if request.method == 'TRACE':
        #TODO - return any data that may have been sent with request
        return response(request.build_full_uri(), "text/plain", 200)

    if request.method == 'POST':
        try:
          #We first do a bunch of validity checks to pull the relevant information from the JSON passed in.
          try:
              #with open(os.path.join(os.path.dirname(__file__), "data.txt"), "a+") as outfile:
                #outfile.write("\r\n\r\n[%s]\r\n"%(datetime.now().isoformat()))
                #json.dump(request.POST["data"], outfile)
                #outfile.write(request.body)
              jsonDict = json.loads(request.POST["data"])
          except Exception as e:
              log_error(e)
              return image_failure(request, "The value for HTTP body could not be interpreted as a valid JSON structure")

          if "geolocation" not in jsonDict:
              return image_failure(request, "Could not find required key 'geolocation' in input")
          geodict = jsonDict["geolocation"]

          if "lat" not in geodict:
              return image_failure(request, "Could not find requred key 'lat' in 'geolocation'")
          latitude = (geodict["lat"])

          if "long" not in geodict:
              return image_failure(request, "Could not find required key 'long' in 'geolocation'")
          longitude = (geodict["long"])

          #Name and Tags are optional parameters
          if "name" not in jsonDict:
              image_name = "Untitled image from device"
          else:
              image_name = jsonDict["name"]

          if "tags" in jsonDict:
              tags = tag_utils.TagsFromText(",".join(jsonDict["tags"]))

          if "description" in jsonDict:
              try:
                  image_description = jsonDict["description"]
              except Exception as e:
                  log_error(e)
                  return rest_failure(request)

          image = request.FILES['image']

          img = wainz.models.Image()

          try:
              extension = image.name.split('.')[1]
          except IndexError:
              extension = 'jpg' #some form of detection would be better

          hashname = random.getrandbits(128)
          img.submission_date = timezone.now()
          img.image_name = image_name
          img.latitude = latitude
          img.longitude = longitude
          img.image_description = image_description
          img.extension = extension
          img.image_path = hashname
          img.submitter = User.objects.get(username__exact='mobile')
          img.save()

          for tag in tags:
              img.tags.add(tag)
          img.save()

          ImagePath = os.path.join(settings.STATIC_ROOT, "uploaded-images/%s.%s" % (hashname, extension))
          ThumbImagePath = os.path.join(settings.STATIC_ROOT, "uploaded-images/%s-thumb.%s" % (hashname, extension))
          try:
              with open(ImagePath, "wb+") as img_file:
                  img_file.write(image.read())
          except Exception as e:
              log_error(e)
              return rest_failure(request)

          thumbwidth = 240.0
          thumbheight = 180.0
          im = PIL.Image.open(ImagePath)
          wfactor = thumbwidth/im.size[0]
          hfactor = thumbheight/im.size[1]

          if wfactor > hfactor:
            im = im.resize((int(im.size[0]*wfactor), int(im.size[1]*wfactor)), PIL.Image.ANTIALIAS)
            im = im.crop((0, int((im.size[1] - thumbheight)/2), im.size[0],  int(im.size[1] - (im.size[1] - thumbheight)/2)))
          else:
            im = im.resize((int(im.size[0]*hfactor), int(im.size[1]*hfactor)), PIL.Image.ANTIALIAS)
            im = im.crop((int((im.size[0] - thumbwidth)/2), 0 ,  int(im.size[0] - (im.size[0] - thumbwidth)/2), im.size[1]))

          im.save(ThumbImagePath)

          return rest_success(request, img.id)

        except Exception as e:
            log_error(e)
            return rest_failure(request)

def rest_success(request, img_id):
    '''
    Successful rest calls always return the same thing at the moment
    '''
    respDict = {}
    respDict["status"] = "OK"
    respDict["error_message"] = ""
    #respDict["url"] = "/image/%s" % img_id
    respDict["url"] = reverse('wainz.views.image', args=[img_id])
    responseData = json.dumps(respDict)
    response = HttpResponse(responseData, "application/json", 200)
    return response

def image_failure(request, message):
    '''
    A failure in the api should return 200 with the error message, rather than
    returning the http error code, which isn't really restful, but it was breaking
    integration. I figure we prefer an API that actually integrates to one that
    uncomprimisingly follows rest techniques
    '''
    respDict = {}
    respDict["status"] = "ERROR"
    respDict["error_message"] = message
    respDict["url"] = request.build_absolute_uri()
    responseData = json.dumps(respDict)
    response = HttpResponse(responseData, "application/json", 200)
    return response

def rest_failure(request):
    '''
    This is an actual, legitimate exception. As in our code threw an unhandled exception.
    '''
    respDict = {}
    respDict["status"] = "ERROR"
    respDict["error_message"] = "An unexpected error occurred on the server end. Please contact the server administrator"
    respDict["url"] = request.build_absolute_uri()
    responseData = json.dumps(respDict)
    response = HttpResponse(responseData, "application/json", 200)
    return response

def log_error(msg):
    with open(os.path.join(os.path.dirname(__file__), "log.txt"), "a+") as err_log:
        err_log.write("\r\n[%s]%s"%(datetime.now().isoformat(), msg))
