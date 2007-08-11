from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseServerError
import django.newforms as forms
from django.conf import settings
from django.shortcuts import render_to_response
from person_forms import SignupForm, PaymentForm
from .. import helpers
from ..models import Account, Person, RecurringPayment
from account.lib.payment.errors import PaymentRequestError, PaymentResponseError
from django.core import mail

def upgrade(request):
    return HttpResponse('upgrade')

def _email_cancel_error_to_admin(account, old_payment, new_payment=None):
    mail.mail_admins(
        "! Payment Cancel Error", 
        """
        There was an error canceling payment for %s.
        Account Id: %i
        Old Payment Gateway Token: %s
        New Payment Gateway Token: %s
        
        This should NOT ever happen unless there is a problem with
        the gateway interface on your end, or the payment gateway 
        changed their API.
        """ % (
            account.name,
            account.id,
            old_payment.gateway_token,
            getattr(new_payment, 'gateway_token', '(no new payment)')
            )
    )
    
def _email_create_error_to_admin(account=None):
    mail.mail_admins(
        "! Payment Create Error", 
        """
        There was an error canceling payment for %s.
        Account Id: %s
        
        This should NOT ever happen unless there is a problem with
        the gateway interface on your end, or the payment gateway 
        changed their API.
        """ % (
            getattr(account, 'name', '(No account yet)'),
            str(getattr(account, 'id', '(No account yet)')),
            )
    )

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
                    _email_cancel_error_to_admin(
                        request.account,
                        old_payment, 
                        new_payment
                    )
                    return helpers.render(
                        request,
                        'account/payment_cancel_error.html',
                        {'recurring_payment': old_payment}
                    )
                
            except PaymentResponseError:
                _email_create_error_to_admin(request.account)
                return helpers.render(
                    request,
                    'account/payment_create_error.html'
                )
            
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
                _email_create_error_to_admin()
                return helpers.render(
                    request,
                    'account/payment_create_error.html'
                )
            
            except PaymentRequestError:
                # The payment gateway rejected our request.
                # Most likely a user input error.
                pass
    else:
        form = SignupForm(
            get_card_info
        )
        
    return render_to_response(
        'account/signup_form.html', 
        {'form': form}
    )

    
    
