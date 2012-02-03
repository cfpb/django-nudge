from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from server import process_batch

@csrf_exempt
def batch(request):
    batch = request.POST['batch']
    result = process_batch(batch)
    return HttpResponse(result)