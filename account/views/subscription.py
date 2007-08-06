from django.http import HttpResponse
import django.newforms as forms
from django.shortcuts import render_to_response
from person_forms import SignupForm
from .. import helpers
from ..models import Account, Person, RecurringPayment

def upgrade(request):
    return HttpResponse('upgrade')

def create(request, level):
    if request.method == 'POST':
        pass
    else:
        form = SignupForm()
        
        
    return render_to_response(
        'account/signup_form.html', 
        {'form': form}
    )

    
    
