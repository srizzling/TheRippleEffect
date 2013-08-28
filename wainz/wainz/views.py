from django.template import RequestContext
from wainz.models import Image, ImageComment, Tag
from wainz.forms import ContactForm, CaptchaForm
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout as internal_logout
from django.contrib.auth.models import User
from django.shortcuts import render, render_to_response
from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.models import get_current_site

from voting.models import Vote

from datetime import datetime
from django.utils.timezone import utc
import math
import json
import search_utils
import rest
import geofilter
import tag_utils
import os
import base64
import random


def add_comment(request):
    """
    Adds a comment to an image. This is only accessible from an individual image
    page, via and ajax call. We don't really mind too much about error handling
    at this point because any ajax call that fails will just show an error message
    when it picks up the 500, rather than explode anything.
    """
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('wainz.views.composite'))
    else:
        img_id = request.POST['id']
        try:
            img = Image.objects.get(pk=img_id)
        except:
            return HttpResponseRedirect(reverse('wainz.views.composite'))
        comment_text = request.POST['comment']
        #TODO sanitize input
        comment = ImageComment()
        comment.submission_date = timezone.now()
        comment.comment_text= comment_text
        comment.image_id = img_id
        comment.submitter_id = int(request.POST['uid'])
        comment.save()
        return rest.rest_success(request, img_id)

def resources(request):
    return render_to_response('wainz/resources.html', {}, context_instance = RequestContext(request))

def facts(request):
    return render_to_response('wainz/facts.html', {}, context_instance = RequestContext(request))

def reports(request):
    return render_to_response('wainz/reports.html', {}, context_instance = RequestContext(request))

def media(request):
    return render_to_response('wainz/media.html', {}, context_instance = RequestContext(request))

def pollution(request):
    return render_to_response('wainz/wainz_cms/pollution.html', {}, context_instance = RequestContext(request))

def uav(request):
    return render_to_response('wainz/uav.html', {}, context_instance = RequestContext(request))

def mobileapps(request):
    return render_to_response('wainz/mobileapps.html', {}, context_instance = RequestContext(request))

def howtohelp(request):
    return render_to_response('wainz/howtohelp.html', {}, context_instance = RequestContext(request))

def imggallery(request):
    context = {}
    images = ordered_images(0, 12, request.user)
    context["images_and_votes"] = enumerate(images)
    context["images_length"] = len(images)
    return render_to_response('wainz/imggallery.html', context, context_instance = RequestContext(request))

def approve(request, img_id):
    """
    If the user object processed for this request context is a staff member,
    then the image with corresponding ID will have its is_approved field set
    to true.
    """
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse('wainz.views.composite'))
    else:
        image = Image.objects.get(pk=img_id)
        image.is_approved=True
        image.save()
        return HttpResponseRedirect(reverse('wainz.views.approve_images'))


def approve_images(request):
    """
    Open the tab where you can approve images
    """
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse('wainz.views.composite'))
    else:
        images = Image.objects.filter(is_approved=False).order_by('-submission_date')
        ctx = {"images":images}
        return render_to_response('wainz/approve_images.html',ctx, context_instance = RequestContext(request))


def add_tag(request):
    """
    Adds a tag onto an image. Currently only accessible from an individual
    image page. This shares a lot of characteristics with adding a comment and
    could be generalised a bit better.
    """
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('wainz.views.composite'))
    else:
        img_id = request.POST['id']
        try:
            img = Image.objects.get(pk=img_id)
        except:
            return HttpResponseRedirect(reverse('wainz.views.composite'))
        tag_val = request.POST['tag']
        try:
            tag = tag_utils.TagsFromText(tag_val)[0]
            added = True
            img.tags.add(tag)
            img.save()
        except:
            added = False
        resp = rest.rest_success(request, img_id)
        respJson = json.loads(resp.content)
        respJson['added'] = added
        resp.content = json.dumps(respJson)
        return resp

def contact(request):
    """
    Returns the contact information page.
    """
    if request.method == 'POST': # If the form has been submitted...
        form = ContactForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            fullname = form.cleaned_data['fullname']
            email = form.cleaned_data['email']
            topic = form.cleaned_data['topic']
            message = form.cleaned_data['message']
            reply_needed = form.cleaned_data['reply']
            tmp_message = "Message From: " + fullname + "\n\n"
            tmp_message += "Email Address: " + email + "\n\n"
            if reply_needed:
                tmp_message += "Reply Needed: Yes\n\n--------------------\n\n"
            else:
                tmp_message += "Reply Needed: No\n\n--------------------\n\n"

            subject = 'Wainz Webform: '+topic
            message = tmp_message + message
            from_email = 'noreply@wainz.org.nz'
            recipient_list = ['wai.newzealand@gmail.com']

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            return HttpResponseRedirect('thanks/') # Redirect after POST
    else:
        form = ContactForm() # An unbound form

    return render(request, 'wainz/contact.html', { 'form': form, })

def our_friends(request):
    """
    Returns the our friends page.
    """   
    return render_to_response('wainz/our_friends.html', {}, context_instance = RequestContext(request))

def image(request, img_id):
    """
    Returns a page displaying a single image, along with all associated comments, tags, and votes.
    """
    image = Image.objects.get(pk=img_id)
    if request.user.is_staff or image.is_approved:
        comments = ImageComment.objects.filter(image_id=img_id).order_by('-submission_date')
        comments_and_votes = Vote.objects.get_weighted_scores_in_bulk(comments, request.user)

        ctx = {"img":image,
               "comments_and_votes":comments_and_votes,
               "image_tags":image.tags.all(),
               "all_tags":Tag.objects.all(),
               "site":get_current_site(request)
              }
        return render_to_response('wainz/image.html', ctx , context_instance = RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('wainz.views.composite'))

def ordered_images(start, max_count, current_user=None):
    images = Image.objects.order_by('-submission_date').filter(is_approved=True)
    votes_and_images = Vote.objects.get_weighted_scores_in_bulk(images, current_user)
    return votes_and_images[start:max_count]


def image_display(start, end, user=None):
    """
    Displays a list of images that have been uploaded by a given user, or all users if the user
    param is None. Also specified are the start and end splice points of the list of images returned,
    allowing you to limit or offset the images returned.
    """
    if user != None:
        images = Image.objects.filter(submitter_id = user.id).order_by('-submission_date')[start:end]
    else:
        images = Image.objects.order_by('-submission_date')[start:end]
    rows = {}
    #Initialise lists
    for i in xrange(int(math.ceil(len(images)/3.0))): rows[i] = []
    #applies the lambda function to put each element into it's correct row
    map((lambda (idx, elem): rows[idx/3].append(elem)), enumerate(images))
    return rows

def images_for_user(request, uname):
    """
    A helper/potentially entirely redundant function that returns all of a users images, accessed from
    the 'display your images' drop down option
    """
    try:
        user = User.objects.get(username=uname)
    except Exception as user_does_not_exist:
        return render_to_response('wainz/image_list.html', {"rows":[]} , context_instance = RequestContext(request))
    return render_to_response('wainz/image_list.html', {"rows":image_display(0, 10000, user)} , context_instance = RequestContext(request))


def image_list(request):
    """
    Returns the latest 30 images submitted
    """
    return render_to_response('wainz/image_list.html', {"images_and_votes": ordered_images(0, 30, request.user)}, context_instance = RequestContext(request))


def composite(request):
    context = {}
    images = ordered_images(0, 12, request.user)
    context["images_and_votes"] = enumerate(images)
    context["images_length"] = len(images)
    now = datetime.utcnow().replace(tzinfo=utc)
    latlngs = search_utils.filter_date(search_utils.min_date, now)
    points = [search_utils.to_map_point(image) for image in latlngs]
    context["latLngs"] = points
    return render_to_response('wainz/composite.html',  context, context_instance = RequestContext(request))


def logout(request):
    """
    Logs the current user out.
    """
    return internal_logout(request, next_page = reverse('wainz.views.composite'), redirect_field_name = 'next')

@csrf_exempt
def more_images(request, count):
    context = {}
    images = ordered_images(int(count)*12, (int(count)+1)*12, request.user)
    context["images_and_votes"] = enumerate(images)
    context["images_length"] = len(images)
    if len(images) > 0:
        return render_to_response('wainz/components/image_list.html', context, context_instance = RequestContext(request))
    else:
        return HttpResponse("false", "application/json", "200")

def reject(request, img_id):
    """
    If the request context's user is staff, then the image with given
    ID be erased (i.e. form disc and database)
    """
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse('wainz.views.composite'))
    else:
        img = Image.objects.get(id=img_id)
        os.remove(os.path.join(settings.STATIC_ROOT, "uploaded-images", "%s.%s" % (img.image_path, img.extension)))
        os.remove(os.path.join(settings.STATIC_ROOT, "uploaded-images", "%s-thumb.%s" % (img.image_path, img.extension)))
        img.delete()
        return HttpResponseRedirect(reverse('wainz.views.approve_images'))

def register_user(request):
    if request.method == "POST":
        try:
          uname = request.POST["username"]
          passwd = request.POST["password1"]
          email = request.POST["email"]
          new_user = User.objects.create_user(uname, email, passwd)
          new_user.is_active = new
          user.save()
        except Exception as e:
          return HttpResponseRedirect(reverse('registration_register'))
        return HttpResponseRedirect(reverse('registration_complete'))
    else:
        return HttpResponseRedirect(reverse('wainz.views.composite'))


def search(request):
    """
    Searches images for the following possible criteria:
        * Date time | all images between two dates
        * Location  | all images within one to many 'geofilters' which are a lat/lng point and radius
        * Tag       | all images matching either all, or at least one, tag, depending on the search conjunctivity
    Currently returns map points, as it's only used by Maps, but is searching images then transforming them,
    so could easily be factored more generally (indeed, it probably should...) 
    """
    #TODO - move these into a better/more extensible location
    geofiltered = []
    datefiltered = []
    tagfiltered = []

    if request.POST["geo_filter"] == "true":
        f_count = request.POST["filters"]
        filters = []
        for i in xrange(int(f_count)):
            filters.append(geofilter.Geofilter(i, request.POST["filter_"+str(i)+"_rad"], request.POST["filter_"+str(i)+"_lat"], request.POST["filter_"+str(i)+"_lng"]))
        imgs = Image.objects.filter(is_approved = True)
        for gfilter in filters:
            search_result = search_utils.filter_location(gfilter, imgs)        
            geofiltered = set(geofiltered).union(search_result)

    if request.POST["date_filter"] == "true":    
        date_from = datetime.strptime(request.POST["from"], "%d/%m/%Y")
        date_to = datetime.strptime(request.POST["to"], "%d/%m/%Y")
        datefiltered.extend(search_utils.filter_date(date_from, date_to))

    if request.POST["tag_filter"] == "true":
        tags = [x for x in request.POST["tags"].split(',') if x]
        for img in Image.objects.filter(is_approved = True):
            tag_matches = map((lambda t : t in [x.tag_text for x in img.tags.all()]), tags)
            if len(tag_matches) == 0: continue
            conjunctive = request.POST["conjunctive"] == 'true'
            if(conjunctive and all(tag_matches)):
                tagfiltered.append(img)
            elif(not conjunctive and any(tag_matches)):
                tagfiltered.append(img)
        print tagfiltered           

    latlngs = Image.objects.filter(is_approved = True)
    #TODO - refactor meeeeee
    if len(geofiltered) > 0: latlngs = set(latlngs).intersection(set(geofiltered))
    if len(datefiltered) > 0: latlngs = set(latlngs).intersection(set(datefiltered))
    if len(tagfiltered) > 0: latlngs = set(latlngs).intersection(set(tagfiltered))
    if len(geofiltered) + len(datefiltered) + len(tagfiltered) == 0: latlngs = []
    respDict = {}
    points = [search_utils.to_map_point(image) for image in latlngs]
 
    respDict["points"] = points

    resp = HttpResponse(json.dumps(respDict), "application/json", 200)
    return resp

def raw_report(request):
    with open(os.path.join(os.path.dirname(__file__), "raw_report.txt")) as raw_in:
        report = raw_in.read()
    return HttpResponse(report, "application/json", 200)

def report_confirm(request):
    """
    After a report's content has been selected we need to return the json
    for the corresponding objects. This function should only ever be called
    after a submission from report_deta
    """
    if request.method == 'POST':
        outputJSON = {}
        outputJSON["title"] = request.POST["title"]
        outputJSON["abstract"] = request.POST["abstract"]
        outputJSON["keywords"] = request.POST["keywords"]
        outputJSON["images"] = imageDict = []
        imgs = int(request.POST["image_length"])
        for idx in xrange(imgs):
            img_id = int(request.POST[str(idx)+"-id"])
            thisImg = {}
            thisImg["location"] = request.POST[str(idx)+"-location"]
            thisImg["caption"] = request.POST[str(idx)+"-caption"]
            img = Image.objects.get(pk=img_id)
            thisImg["lat"] = str(img.latitude)
            thisImg["lng"] = str(img.longitude)
            thisImg["date"] = img.submission_date.isoformat()
            thisImg["extension"] = img.extension
            with open(os.path.join(settings.STATIC_ROOT, "uploaded-images/%s.%s" % (img.image_path, img.extension)), "rb") as imgdata:
                print "reading %s" % imgdata
                imgbin = imgdata.read()
                print "encoding..."
                thisImg["base64"] = base64.b64encode(imgbin)
                print "done"
            imageDict.append(thisImg)
        with open(os.path.join(os.path.dirname(__file__), "raw_report.txt"), "w+") as raw_out:
            raw_out.write(json.dumps(outputJSON))
        return HttpResponse(json.dumps(outputJSON), "application/json", 200)
    else:
        return HttpResponseRedirect(reverse('wainz.views.contact'))


def report_details(request):
    """
    Return the sUAVe report generation confirmation and further detail form
    """
    if request.method == 'POST':
        ids_as_list = request.POST["ids"]
        ids = [int(idx) for idx in ids_as_list.split(',') if idx]
        selected_image_set = [Image.objects.get(pk=idx) for idx in ids]
        ctx = {"selected_image_set":enumerate(selected_image_set), "selected_image_set_length":len(selected_image_set)}
        return render_to_response("wainz/suave_report.html", ctx, context_instance = RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('wainz.views.contact'))


def report_select(request):
    """
    Return the sUAVe report image selector
    """  
    t = loader.get_template("wainz/search_form.html")
    ctx = Context({})
    search_form = t.render(ctx)
    latlngs = Image.objects.all()
    points = [search_utils.to_map_point(image) for image in latlngs]
    return render_to_response("wainz/suave_select.html", {"search_form":search_form, "latLngs":points, "typeAheadTags":Tag.objects.all()}, context_instance = RequestContext(request))


def thanks(request):
    return render_to_response('wainz/thanks.html', {}, context_instance = RequestContext(request))


'''
Login requred non-ajax accessible pages
'''
#@login_required
def submit(request):
    """
    Saves the uploaded image to a temporary location, and redirects the user
    to a details page, where they fill in name, tags, geolocation, and so on.
    """
    if request.POST:
        form = CaptchaForm(request.POST, request.FILES)
        if form.is_valid():
            image = request.FILES['singleImage']
            extension = image.name.split('.')[1]
            hashname = random.getrandbits(128)
            with open(os.path.join(settings.STATIC_ROOT, "tmp/%s.%s" % (hashname, extension)), "w+") as imagePath:
                imagePath.write(image.read())

            ctx = RequestContext(request, {"hash":hashname, "extension":extension})
            template = loader.get_template("wainz/submission_details.html")

            return HttpResponse(template.render(ctx))
    else:
        form = CaptchaForm()

    return render_to_response("wainz/submit.html", dict(form=form), context_instance = RequestContext(request))

#@login_required
def submit_details(request):
    return render_to_response("wainz/submit_details.html", {}, context_instance = RequestContext(request))

def maps(request):
    """
    Converts all images into google maps compatible points, and renders the maps and search sidebar
    html componenents
    """
    #convert image locations to google maps parsable points
    now = datetime.utcnow().replace(tzinfo=utc)
    latlngs = search_utils.filter_date(search_utils.min_date, now)
    points = [search_utils.to_map_point(image) for image in latlngs]
    #load the search form sidebar
    t = loader.get_template("wainz/search_form.html")
    ctx = Context({})
    search_form = t.render(ctx)

    return render_to_response('wainz/maps.html', {"latLngs":points, "search_form":search_form, "typeAheadTags":Tag.objects.all()}, context_instance = RequestContext(request))

