from django.http import HttpResponse
from .. import helpers

def upgrade(request):
    return HttpResponse('upgrade')