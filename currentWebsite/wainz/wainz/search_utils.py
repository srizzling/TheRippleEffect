from wainz.models import Image
from datetime import datetime
from django.utils.timezone import utc
import math
from django.conf import settings

min_date = datetime(1900, 1, 1)
min_date = min_date.replace(tzinfo=utc)

def filter_date(date_from, date_to):
    '''
    Will filter all images currently in the database for images with a submission_date property
    between date_from and date_to
    '''
    latlngs = []
    for image in Image.objects.filter(submission_date__lte = date_to, submission_date__gte = date_from, is_approved = True):
        latlngs.append(image)
    return latlngs

def filter_location(gfilter, latlngs):
    '''
    Finds all images in the given list whose lat/long points lay within the radius of the location filter
    gfilter, using the Haversine distance formula

    The geofilter is a dict that contains lat, lng, and rad, which correspond to latitude, longitude and radius
    '''
    filtered = []
    f_lat = gfilter.lat
    f_lng = gfilter.lng
    r_earth = 6371
    for image in latlngs:
        lat = float(image.latitude)
        lng = float(image.longitude)
        d_lat = math.radians((f_lat-lat))
        d_lng = math.radians((f_lng-lng))
        #magical math happens here
        a = math.sin(d_lat/2) * math.sin(d_lat/2) + math.cos(math.radians(lat)) * math.cos(math.radians(f_lat)) * math.sin(d_lng/2) * math.sin(d_lng/2)
        c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
        dist = r_earth*c*1000 #in metres
        if dist < gfilter.rad:
            filtered.append(image)
    return filtered

def to_map_point(image):
    """
    Stringifies an image object to a dictionary, ready to be used by the maps javascript
    """
    latlng = {}
    latlng["id"] = int(image.id)
    latlng["path"] = settings.STATIC_URL + 'uploaded-images/' + str(image.image_path)
    latlng["lat"] = str(image.latitude)
    latlng["lng"] = str(image.longitude)
    latlng["image_name"] = str(image.image_name)
    latlng["extension"] = str(image.extension)
    return latlng
