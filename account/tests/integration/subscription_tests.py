import re
from datetime import date
from django.test import TestCase, Client
from django.core import mail
from django.conf import settings
from account.models import Person, Account, RecurringPayment
from base import IntegrationTest
import django.newforms as forms
import causes
import effects
import security
from account.tests.mocks.payment_gateway import MockGateway
from account.models import recurring_payment
from account.lib.payment.errors import PaymentRequestError, PaymentResponseError

from account.tests.mocks import subscription_levels
CREATE_PATH = '/account/create/%i/'
CHANGE_PM_PATH = '/account/change_payment_method/'

    
############################
# Causes and Effects
############################

def payment_request_error(client, request):
    recurring_payment.gateway.error = PaymentRequestError
    return client, request

def payment_response_error(client, request):
    recurring_payment.gateway.error = PaymentResponseError
    return client, request

def payment_response_error_on_cancel(client, request):
    recurring_payment.gateway.reset()
    recurring_payment.gateway.error_on_cancel = PaymentResponseError
    return client, request
        
def gateway_cancel_called(client, response, testcase):
    assert recurring_payment.gateway.cancel_payment_called

def account_has_no_payment_method(client, parameters):
    try:
        RecurringPayment.objects.get(account__pk = 1).delete()
    except RecurringPayment.DoesNotExist:
        pass
    return client, parameters

def account_has_payment_method(client, parameters):
    account_has_no_payment_method(client, parameters)
    Account.objects.get(pk = 1).recurring_payment = RecurringPayment(
        name = 'Bob Jones',
        period = 1,
        amount = '$10.00',
        number = '********1234',
        token = 2,
        gateway_token = '1000',
    )
    return client, parameters
    
domain = '%s.%s' % ('billybob', settings.ACCOUNT_DOMAINS[0])

def delete_test_account(client, request):
    try:
        Person.objects.get(username = 'billybob').delete()
        Account.objects.get(domain = domain).delete()
    except (Person.DoesNotExist, Account.DoesNotExist):
        pass
    return client, request


signup_params_no_cc = dict(
    first_name = 'billy',
    last_name = 'bob',
    email = 'billybob@lala.net',
    username = 'billybob',
    password = 'password',
    password2 = 'password',
    group = 'billybob carpet cleaning',
    timezone = 0,
    subdomain = 'billybob',
    root_domain = 0,
    terms_of_service = True,
)
cc_params = dict(
    card_type = 0,
    card_number = '411111111111',
    card_expiration = date.today()
    
)

change_payment_method_params = dict(
    first_name = 'billy',
    last_name = 'bob',                    
    card_number = '411111111111',
    card_expiration = date.today()    
)
        

class SubscriptionTests(IntegrationTest):
    fixtures = ['test/accounts.json', 'test/people.json']
    def setUp(self):
        recurring_payment.gateway = MockGateway()
        recurring_payment.gateway.reset()
        
    
    ############################
    # Signup Tests
    ############################
    
    def test_signup(self):
        """
        Tests for person_views.login
        """
        #-------------------------------------------------
        # You can't sign up from a domain belonging
        # to an account.
        #-------------------------------------------------
        self.assertState(
            'GET/POST',
            CREATE_PATH % 0,
            [
                causes.person_not_logged_in,
                causes.valid_domain,
            ],
            [
                effects.status(404),
            ]
        )
        
        #-------------------------------------------------
        # Show the signup form
        #-------------------------------------------------
        self.assertState(
            'GET/POST',
            CREATE_PATH % 0,
            [
                causes.no_domain,
                causes.no_parameters,
            ],
            [
                effects.rendered('account/signup_form.html'),
                effects.status(200)
            ]
        )
        
        #-------------------------------------------------
        # If the subscription level is invaid, show 404
        #-------------------------------------------------
        self.assertState(
            'GET/POST',
            CREATE_PATH % 789, # 789 is invalid subscription level
            [
                causes.no_domain,
                causes.no_parameters,
            ],
            [
                effects.status(404)
            ]
        )
        
            
        #-------------------------------------------------
        # If the subscription level is free, a credit
        # card is not required.
        #-------------------------------------------------
        self.assertState(
            'POST',
            CREATE_PATH % 0, # 0 is Free Account
            [
                delete_test_account,
                causes.no_domain,
                causes.params(**signup_params_no_cc),
            ],
            [
                effects.redirected_to_url(
                    "http://%s/" % domain
                ),
                effects.exists(Account, domain = domain),
                effects.exists(Person, email = 'billybob@lala.net'),
            ]
        )
        
        #-------------------------------------------------
        # If the subscription level is NOT free, a credit
        # card IS required.
        #-------------------------------------------------
        self.assertState(
            'POST',
            CREATE_PATH % 1, # 1 is Silver (pay) account
            [
                delete_test_account,
                causes.no_domain,
                causes.params(**signup_params_no_cc),
            ],
            [
                effects.rendered('account/signup_form.html'),
                effects.status(200)
            ]
        )
        
        #-------------------------------------------------
        # If everything validates, create a person, account
        # and recurring payment.
        #-------------------------------------------------
        self.assertState(
            'POST',
            CREATE_PATH % 1, # 1 is Silver (pay) account
            [
                delete_test_account,
                causes.no_domain,
                causes.params(**signup_params_no_cc),
                causes.params(**cc_params),
            ],
            [
                effects.redirected_to_url(
                    "http://%s/" % domain
                ),
                effects.exists(Account, domain = domain),
                effects.exists(Person, email = 'billybob@lala.net'),
                effects.exists(RecurringPayment, name = 'billy bob'),
            ]
        )
        
        #-------------------------------------------------
        # If the gateway returns an unrecognized response,
        # show a special message & email the administrator.
        #-------------------------------------------------
        self.assertState(
            'POST',
            CREATE_PATH % 1, # 1 is Silver (pay) account
            [
                delete_test_account,
                causes.no_domain,
                causes.params(**signup_params_no_cc),
                causes.params(**cc_params),
                payment_response_error
            ],
            [
                effects.outbox_len(1),
                effects.rendered('account/payment_create_error.html'),
            ]
        )
        
        #-------------------------------------------------
        # If the gateway does not accept the payment info,
        # show the form.
        #-------------------------------------------------
        self.assertState(
            'POST',
            CREATE_PATH % 1, # 1 is Silver (pay) account
            [
                delete_test_account,
                causes.no_domain,
                causes.params(**signup_params_no_cc),
                causes.params(**cc_params),
                payment_request_error,
            ],
            [
                effects.rendered('account/signup_form.html'),
                effects.status(200)
            ]
        )
        
        
        
    ############################
    # Change Payment Method Tests
    ############################
        
    def test_change_payment_method(self):
        """
        """
        security.check(self, CHANGE_PM_PATH)
        
        #-------------------------------------------------
        # The form is shown
        #-------------------------------------------------
        self.assertState(
            'GET/POST',
            CHANGE_PM_PATH,
            [
                causes.valid_domain,
                causes.owner_logged_in,
                causes.no_parameters,
            ],
            [
                effects.rendered('account/payment_method_form.html'),
                effects.status(200)
            ]
        )
        
            
        #-------------------------------------------------
        # The form is shown if input is invalid
        #-------------------------------------------------
        self.assertState(
            'POST',
            CHANGE_PM_PATH,
            [
                causes.valid_domain,
                causes.owner_logged_in,
                causes.no_parameters,
                causes.params(
                    first_name = 'billy',
                    last_name = 'bob',                    
                    card_number = '411111111111',
                    card_expiration = None
                )
            ],
            [
                effects.rendered('account/payment_method_form.html'),
                effects.status(200)
            ]
        )
        
        #-------------------------------------------------
        # If input is valid, a RecurringPayment is created
        #-------------------------------------------------
        self.assertState(
            'POST',
            CHANGE_PM_PATH,
            [
                causes.valid_domain,
                causes.owner_logged_in,
                causes.no_parameters,
                causes.params(
                    first_name = 'billy',
                    last_name = 'bob',                    
                    card_number = '411111111111',
                    card_expiration = date.today()
                ),
                account_has_no_payment_method,
            ],
            [
                effects.exists(
                    RecurringPayment, 
                    account__domain = 'starr.localhost.com'
                ),
                effects.rendered('account/payment_method_form.html'),
                effects.status(200)
            ]
        )
        
            
        #-------------------------------------------------
        # If input is valid, and a RecurringPayment exists,
        # the old RecurringPayment is deleted and a new one
        # is created.
        #-------------------------------------------------
        self.assertState(
            'POST',
            CHANGE_PM_PATH,
            [
                causes.valid_domain,
                causes.owner_logged_in,
                causes.no_parameters,
                causes.params(**change_payment_method_params),
                account_has_payment_method,
            ],
            [
                gateway_cancel_called,
                effects.exists(
                    RecurringPayment, 
                    account__domain = 'starr.localhost.com'
                ),
                effects.count(1, RecurringPayment, name = 'billy bob'),
                effects.rendered('account/payment_method_form.html'),
                effects.status(200)
            ]
        )
        
        #-------------------------------------------------
        # If we get a PeymentRequestError, it means that
        # the user probably entered some invalid info.
        # If the payment gateway returned this error, a 
        # RecurringPayment is NOT created.
        #-------------------------------------------------
        
        self.assertState(
            'POST',
            CHANGE_PM_PATH,
            [
                causes.valid_domain,
                causes.owner_logged_in,
                causes.no_parameters,
                causes.params(**change_payment_method_params),
                account_has_no_payment_method,
                payment_request_error,
            
            ],
            [
                gateway_cancel_called,
                effects.does_not_exist(
                    RecurringPayment, 
                    account__domain = 'starr.localhost.com'
                ),
                effects.does_not_exist(
                    RecurringPayment, 
                    name = 'billy bob'
                ),
                effects.rendered('account/payment_method_form.html'),
                effects.status(200)
            ]
        )
        
        #-------------------------------------------------
        # If we get a PeymentRequestError, it means that
        # the user probably entered some invalid info.
        # If the payment gateway returned this error, AND a
        # RecurringPayment exists for the account, do NOT
        # delete it.
        #-------------------------------------------------
        self.assertState(
            'POST',
            CHANGE_PM_PATH,
            [
                causes.valid_domain,
                causes.owner_logged_in,
                causes.no_parameters,
                causes.params(**change_payment_method_params),
                account_has_payment_method,
                payment_request_error,
            
            ],
            [
                gateway_cancel_called,
                effects.exists(
                    RecurringPayment, 
                    account__domain = 'starr.localhost.com'
                ),
                effects.count(1, RecurringPayment, name = 'Bob Jones'),
                effects.count(0, RecurringPayment, name = 'billy bob'),
                effects.rendered('account/payment_method_form.html'),
                effects.status(200)
            ]
        )
        
        #-------------------------------------------------
        # If there is a PaymentResponse error, it means
        # we couldn't understand the response from the 
        # gateway. So a special error page is displayed
        # and the administrator is emailed.
        #-------------------------------------------------
        
        self.assertState(
            'POST',
            CHANGE_PM_PATH,
            [
                causes.valid_domain,
                causes.owner_logged_in,
                causes.no_parameters,
                causes.params(**change_payment_method_params),
                account_has_payment_method,
                payment_response_error,
            
            ],
            [
                gateway_cancel_called,
                effects.exists(
                    RecurringPayment, 
                    account__domain = 'starr.localhost.com'
                ),
                effects.outbox_len(1),
                effects.count(1, RecurringPayment, name = 'Bob Jones'),
                effects.count(0, RecurringPayment, name = 'billy bob'),
                effects.rendered('account/payment_create_error.html'),
                effects.status(200)
            ]
        )
        
        #-------------------------------------------------
        # If there is a PaymentResponse error when canceling
        # an existing payment, it is very bad. It means that 
        # the customer will be billed twice! So we diaplay a
        # special error message, and email the administrator.
        #-------------------------------------------------
        self.assertState(
            'POST',
            CHANGE_PM_PATH,
            [
                causes.valid_domain,
                causes.owner_logged_in,
                causes.no_parameters,
                causes.params(**change_payment_method_params),
                account_has_payment_method,
                payment_response_error_on_cancel,
            
            ],
            [
                gateway_cancel_called,
                effects.exists(
                    RecurringPayment, 
                    account__domain = 'starr.localhost.com'
                ),
                effects.outbox_len(1),
                effects.count(0, RecurringPayment, name = 'Bob Jones'),
                effects.count(1, RecurringPayment, name = 'billy bob'),
                effects.rendered('account/payment_cancel_error.html'),
                effects.status(200)
            ]
        )
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
