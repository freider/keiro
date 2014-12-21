# Create your views here.
import os
import statsapp.models as m
from django.http import HttpResponse
from django.conf import settings


def delete(request, rid):
    rec = m.Record.objects.get(pk=rid)
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
