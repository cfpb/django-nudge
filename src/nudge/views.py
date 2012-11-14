from django.db import transaction
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from nudge.server import process_batch, versions

try:
    import simplejson as json
except ImportError:
    import json


@csrf_exempt
def batch(request):
    key = settings.NUDGE_KEY.decode('hex')
    result = process_batch(key, request.POST['batch'], request.POST['iv'])
    return HttpResponse(result)


@csrf_exempt
def check_versions(request):
    keys = json.loads(request.POST['keys'])
    result = versions(keys)
    return HttpResponse(result)
