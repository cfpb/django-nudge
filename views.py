from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def batch(request):
    return HttpResponse(request.POST['items'])
