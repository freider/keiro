from django.conf.urls.defaults import *
from django.conf import settings
from statsapp import models
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    (
        r'^/?$', 'django.views.generic.list_detail.object_list',
        {'queryset': models.Record.objects.order_by('-date')}
    )
)

urlpatterns += patterns(
    '',
    url(
        r'^video/(?P<path>.*)$', 'django.views.static.serve',
        {
            'document_root': settings.KEIRO_VIDEO_PATH,
            'show_indexes': True
        }
    ),
)
