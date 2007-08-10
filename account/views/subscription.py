from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseServerError
import django.newforms as forms
from django.conf import settings
from django.shortcuts import render_to_response
from person_forms import SignupForm, PaymentForm
from .. import helpers
from ..models import Account, Person, RecurringPayment
from account.lib.payment.errors import PaymentRequestError, PaymentResponseError

def upgrade(request):
    return HttpResponse('upgrade')

def change_payment_method(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            
            old_payment = request.account.recurring_payment
            
            try:
                # Create new recurring transaction:
                new_payment = form.save_payment(
                    request.account,
                    request.account.subscription_level,
                    commit = False
                )
                
                # Change the DB records 
                if old_payment: 
                    old_payment.delete()
                new_payment.save()
                
                # Cancel the old recurring transaction:
                try:
                    if old_payment: 
                        old_payment.cancel()
                except (PaymentResponseError, HttpResponseServerError):
                    # Possibly add more user-friendly error message.
                    return HttpResponseServerError()
                
            except PaymentResponseError:
                return HttpResponseServerError()
            
            except PaymentRequestError:
                pass
            
            
                
    else:
        form = PaymentForm()
        
    return helpers.render(
        request, 
        'account/payment_method_form.html', 
        { 'form': form }
    )
    
    
    
def create(request, level):
    try:
        subscription_level = settings.SUBSCRIPTION_LEVELS[int(level)]
    except (IndexError, ValueError):
        raise Http404
    
    get_card_info = subscription_level.get('price')
    
    if request.method == 'POST':
        form = SignupForm(
            get_card_info,
            request.POST,
        )
        if form.is_valid():
            person, account = None, None
            try:
                account = form.save_account(level)
                person = form.save_person(account)
                payment = form.save_payment(account, subscription_level)
                
                return HttpResponseRedirect(
                    'http://%s/' % form.cleaned_data['domain']
                )
            except ValueError:
                # Either person or account could not be created.
                if person and person.id:
                    person.delete()
                if account and account.id:
                    account.delete()
                    
            except PaymentResponseError:
                # The payment gateway returned an unknown response.
                return HttpResponseServerError()
            
            except PaymentRequestError:
                # The payment gateway rejected our request.
                pass
    else:
        form = SignupForm(
            get_card_info
        )
        
    return render_to_response(
        'account/signup_form.html', 
        {'form': form}
    )

    
    
