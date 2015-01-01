# Create your views here.
import os
from statsapp import models
from django.http import HttpResponse
from django.conf import settings
from django.views.generic.list import ListView


def delete(request, rid):
    rec = models.Record.objects.get(pk=rid)
    recrepr = repr(rec)
    extra = ""
    videopath = os.path.join(
        settings.KEIRO_VIDEO_PATH,
        "{}.mp4".format(rid)
    )
    if os.path.exists(videopath):
        os.remove(videopath)
        extra = " and video"
    rec.delete()
    return HttpResponse(
        "Deleted {}{}".format(recrepr, extra)
    )


class RecordListView(ListView):
    queryset = models.Record.objects.order_by('-date')
