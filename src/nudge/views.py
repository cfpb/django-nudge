from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from server import process_batch

from nudge.models import *


SETTINGS, created = Setting.objects.get_or_create(pk=1)

@csrf_exempt
def batch(request):
    key = SETTINGS.local_key.decode('hex')
    result = process_batch(key, request.POST['batch'], request.POST['iv'])
    return HttpResponse(result)
