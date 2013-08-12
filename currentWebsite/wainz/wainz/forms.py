from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.utils import timezone
import wainz.models
import tag_utils
import os.path
import random
import PIL.Image
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from captcha.fields  import CaptchaField

def submission_details(request):
    """
    Saves the temporary image into the db proper, with the detailed fields which
    are required for our image objects.
    """
    if(request.method == 'POST'):
        hashname = request.POST["hash"]
        extension = request.POST["extension"]
        tmpImagePath = os.path.join(settings.STATIC_ROOT, "tmp/%s.%s" % (hashname, extension))
        ImagePath = os.path.join(settings.STATIC_ROOT, "uploaded-images/%s.%s" % (hashname, extension))
        ThumbImagePath = os.path.join(settings.STATIC_ROOT, "uploaded-images/%s-thumb.%s" % (hashname, extension))
        with open(tmpImagePath, "r") as tmpImage:
            with open(ImagePath, "wb+") as image:
                image.write(tmpImage.read())
        os.remove(tmpImagePath)

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

        tag_text = request.POST['tags']
        tags = tag_utils.TagsFromText(tag_text)

        new_entry = wainz.models.Image()
        new_entry.submission_date = timezone.now()
        new_entry.image_name = request.POST["imageName"]
        new_entry.latitude = request.POST["latitude"]
        new_entry.longitude = request.POST["longitude"]
        new_entry.image_description = request.POST["description"]
        new_entry.extension = extension
        new_entry.image_path = hashname
        if request.user.is_authenticated():
            new_entry.submitter = request.user
        else:
            new_entry.submitter = User.objects.get(username__exact='web')
        new_entry.save()
        for tag in tags:
            new_entry.tags.add(tag)
        new_entry.save()
        return HttpResponseRedirect(reverse('wainz.views.composite'))
    else:
        return HttpResponseRedirect(reverse('wainz.views.contact'))


class ContactForm(forms.Form):
    TOPIC_CHOICES = (
        ('Upload Problems', 'Upload Problems'),
        ('Complaints', 'Complaints'),
        ('Enquiry', 'Enquiry'),
        ('Other', 'Other'),
    )

    fullname = forms.CharField(label='Full Name')
    email = forms.EmailField(label='Email Address')
    topic = forms.ChoiceField(label='Concerning', choices=TOPIC_CHOICES)
    message = forms.CharField(label='Description of enquiry', widget=forms.Textarea(attrs={'rows': 5,'style': 'width:340px;'}))
    reply = forms.BooleanField(label='I require a reply', required=False)
    captcha = CaptchaField(label='Enter the characters on the image below to verify this message')

class CaptchaForm(forms.Form):
    singleImage = forms.FileField(label='Select the location of your image')
    captcha = CaptchaField(label='Enter the characters on the image below to verify your submission')
