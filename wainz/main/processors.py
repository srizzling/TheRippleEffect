from django.core.urlresolvers import reverse

def current_url(request):
    return {'current_url': request.get_full_path()}

def tabs(request):
    return {'tabs': [{'name': x[0], 'path': x[1], 'active': request.get_full_path() == x[1]}
        for x in [('Home', reverse('wainz.views.composite')), ('Map', reverse('wainz.views.maps')), ('Submit', reverse('wainz.views.submit')), ('Contact', reverse('wainz.views.contact'))]
    ]}
