from django.db import models
import django.contrib.auth.models
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse
import datetime
import pytz
utc=pytz.UTC

try:
    from functools import total_ordering
except ImportError:
    from utils import total_ordering

class Tag (models.Model):
    tag_text = models.CharField("Tag", max_length=30)
    def __unicode__(self):
        return self.tag_text

@total_ordering
class Image (models.Model):
    submission_date = models.DateTimeField('Date submitted')
    image_name = models.CharField(max_length="100")
    image_path = models.CharField(max_length="80")
    image_description = models.TextField(blank=True, null=True)
    extension = models.CharField(max_length="10")
    latitude = models.DecimalField(decimal_places=10, max_digits=14, default=0)
    longitude = models.DecimalField(decimal_places=10, max_digits=14, default=0)
    submitter = models.ForeignKey(django.contrib.auth.models.User)
    tags = models.ManyToManyField(Tag, blank=True, null=True)
    is_sticky = models.BooleanField('sticky status', default=False, help_text='Makes an image sticky. Sticky images will appear above any non sticky image submissions, regardless of ranking.')
    is_approved = models.BooleanField('approved status', default=False, help_text='Makes an image visible. Images are hidden until approved by a moderator.')

    def __unicode__(self):
        return self.image_name

    def weight(self, vote_sum, vote_num):
        then = self.submission_date
        now = utc.localize(datetime.datetime.today())
        delta = now - then
        return (self.is_sticky, vote_sum * 0.9955 ** delta.days)

    def get_absolute_url(self):
        return reverse('wainz.views.image', args=[(self.id)])

    def __lt__(self, other):
        return submission_date.__lt__(other)

@total_ordering
class ImageComment (models.Model):
    image = models.ForeignKey(Image)
    comment_text = models.CharField("Comment", max_length=500)
    submission_date = models.DateTimeField("Date submitted")
    submitter = models.ForeignKey(django.contrib.auth.models.User)

    def __unicode__(self):
        return self.comment_text

    def get_absolute_url(self):
        #return '/image/%d' % (self.image.id)
        return reverse('wainz.views.image', args=[(self.image.id)])

    def weight(self, vote_sum, vote_num):
        return vote_sum

    def __lt__(self, other):
        return submission_date.__lt__(other)

class UserProfile(models.Model):
    '''
    Represents a user's profile.

    Custom user fields should be added here
    See https://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users for details on why this is necessary.
    '''
    user = models.OneToOneField(django.contrib.auth.models.User)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=django.contrib.auth.models.User, weak=False)
