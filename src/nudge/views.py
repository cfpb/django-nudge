from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from server import process_batch

from nudge.models import *
from reversion.models import Version

from django.conf import settings


@csrf_exempt
def batch(request):
    key = settings.NUDGE_KEY.decode('hex')
    
    result = process_batch(key, request.POST['batch'], request.POST['iv'])
    return HttpResponse(result)


@csrf_exempt
def check_versions(request):
    import pdb;pdb.set_trace()
