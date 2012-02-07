from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from server import process_batch

@csrf_exempt
def batch(request):
    result = process_batch(request.POST['batch'], request.POST['iv'])
    return HttpResponse(result)
