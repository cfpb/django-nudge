import json
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from nudge import server

@csrf_exempt
@transaction.commit_on_success
def batch(request):
    key = settings.NUDGE_KEY.decode('hex')
    result = server.process_batch(key, request.POST['batch'], request.POST['iv'])
    return HttpResponse(result)


@csrf_exempt
def check_versions(request):
    keys = json.loads(request.POST['keys'])
    result = server.versions(keys)
    return HttpResponse(result)
