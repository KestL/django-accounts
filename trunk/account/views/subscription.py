from django.http import HttpResponse
import django.newforms as forms
from .. import helpers
from ..models import Account, Person, RecurringPayment

def upgrade(request):
    return HttpResponse('upgrade')

def create(request, level):
    if request.method == 'POST':
        pass
    else:
        person_form = forms.form_for_model(Person)
        

    
    return HttpResponse('create ' + level)

    
    
