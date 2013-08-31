from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from wainz.models import Image,ImageComment
import voting.views
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'wainz.views.composite'),
    url(r'^maps/$', 'wainz.views.maps'),
    url(r'^contact/$', 'wainz.views.contact'),
    url(r'^contact/thanks/$', 'wainz.views.thanks'),
    url(r'^our_friends/$', 'wainz.views.our_friends'),
    url(r'^resources/$', 'wainz.views.resources'),
    url(r'^facts/$', 'wainz.views.facts'),
    url(r'^media/$', 'wainz.views.media'),
    url(r'^imggallery/$', 'wainz.views.imggallery'),
    url(r'^uav/$', 'wainz.views.uav'),
    url(r'^pollution/$', 'wainz.views.pollution'),

 #    url(r'^pollutioncms/', 'wainz.wainz_cms.pollution'),
    url(r'^mobileapps/$', 'wainz.views.mobileapps'),
    url(r'^howtohelp/$', 'wainz.views.howtohelp'),
    url(r'^reports/$', 'wainz.views.reports'),
    url(r'^submit/$', 'wainz.views.submit'),
    url(r'^search/$', 'wainz.views.search'),
    url(r'^image_list/$', 'wainz.views.image_list'),
    url(r'^more_images/(?P<count>\d+)/$', 'wainz.views.more_images'),
    url(r'^images_for_user/(?P<uname>\w+)$', 'wainz.views.images_for_user'),
    url(r'^report_generation/$', 'wainz.views.report_select'),
    url(r'^report_details/$', 'wainz.views.report_details'),
    url(r'^report_confirm/$', 'wainz.views.report_confirm'),

    #for sUAVe testing
    url(r'^raw_report/$', 'wainz.views.raw_report'),

    #Image details
    url(r'^image/(?P<img_id>\d+)/$', 'wainz.views.image'),
    url(r'^add_comment/$', 'wainz.views.add_comment'),
    url(r'^add_tag/$', 'wainz.views.add_tag'),

    #API goofiness
    url(r'^api/image/$', 'wainz.rest.image'),
    url(r'^api/image$', 'wainz.rest.image'),

    #Submission handling
    url(r'^captcha/', include('captcha.urls')),
    url(r'^image/submission_details/$', 'wainz.forms.submission_details'),

    # Authentication
    url(r'^wlogin/$', 'django.contrib.auth.views.login'),
    url(r'^wlogout/$', 'wainz.views.logout'),

    # Voting - Images
    url(r'^image/(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/$', 'voting.views.vote_on_object',
    {'model':Image, 'template_object_name':'image', 'template_name':'wainz/confirm_vote.html'}),

    # Voting - Comments
    url(r'^image/comments/(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/$', 'voting.views.vote_on_object',
    {'model':ImageComment, 'template_object_name':'image comment', 'template_name':'wainz/confirm_vote.html'}),

    #Approval - Images
    url(r'^approve/$','wainz.views.approve_images'),
    url(r'^approve/(?P<img_id>\d+)/$','wainz.views.approve'),
    url(r'^reject/(?P<img_id>\d+)/$','wainz.views.reject'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # CMS
    url(r'^', include('cms.urls')),
)

# Registration
if settings.HAS_REGISTRATION:
    urlpatterns += patterns('',
        url(r'^accounts/', include('registration.backends.default.urls')),
    )

urlpatterns += staticfiles_urlpatterns()

# CMS
if settings.DEBUG:
    urlpatterns = patterns('',
    url(r'^media2/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'', include('django.contrib.staticfiles.urls')),
) + urlpatterns
