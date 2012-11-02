from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from server import process_batch, versions

from nudge.models import *


from django.conf import settings

import json


@csrf_exempt
def batch(request):
    key = settings.NUDGE_KEY.decode('hex')
    
    result = process_batch(key, request.POST['batch'], request.POST['iv'])
    return HttpResponse(result)


@csrf_exempt
def check_versions(request):
    keys=json.loads(request.POST[u'keys'])
    result=versions(keys)
    return HttpResponse(result)
