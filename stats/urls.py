from django.conf.urls.defaults import *
from statsapp import models
import django
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	(r'^/?$', 'django.views.generic.list_detail.object_list', {'queryset': models.Run.objects.all()})
    # Example:
    # (r'^stats/', include('stats.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
