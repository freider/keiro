from django.conf.urls import url
from django.conf import settings
from statsapp.views import RecordListView

urlpatterns = [
    url(
        r'^/?$', RecordListView.as_view()
    ),
    url(
        r'^video/(?P<path>.*)$', 'django.views.static.serve',
        {
            'document_root': settings.KEIRO_VIDEO_PATH,
            'show_indexes': True
        }
    ),
    url(r'^delete/(?P<rid>\d+)$', 'statsapp.views.delete')
]
