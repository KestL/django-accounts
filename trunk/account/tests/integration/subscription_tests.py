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

    
class SubscriptionTests(IntegrationTest):
    fixtures = ['test/accounts.json', 'test/people.json']
    def setUp(self):
        recurring_payment.gateway = MockGateway()
        recurring_payment.gateway.reset()
        
    
    def test_signup(self):
        """
        Tests for person_views.login
        """
        
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
        
        domain = '%s.%s' % ('billybob', settings.ACCOUNT_DOMAINS[0])
        
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
        
        def clean_db(client, request):
            try:
                Person.objects.get(username = 'billybob').delete()
                Account.objects.get(domain = domain).delete()
            except (Person.DoesNotExist, Account.DoesNotExist):
                pass
            return client, request
            
        self.assertState(
            'POST',
            CREATE_PATH % 0, # 0 is Free Account
            [
                clean_db,
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
        
        self.assertState(
            'POST',
            CREATE_PATH % 1, # 1 is Silver (pay) account
            [
                clean_db,
                causes.no_domain,
                causes.params(**signup_params_no_cc),
            ],
            [
                effects.rendered('account/signup_form.html'),
                effects.status(200)
            ]
        )
        self.assertState(
            'POST',
            CREATE_PATH % 1, # 1 is Silver (pay) account
            [
                clean_db,
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
        
        def payment_request_error(client, request):
            recurring_payment.gateway.error = PaymentRequestError
            return client, request
        def payment_response_error(client, request):
            recurring_payment.gateway.error = PaymentResponseError
            return client, request
        
        self.assertState(
            'POST',
            CREATE_PATH % 1, # 1 is Silver (pay) account
            [
                clean_db,
                causes.no_domain,
                causes.params(**signup_params_no_cc),
                causes.params(**cc_params),
                payment_response_error
            ],
            [
                effects.status(500)
            ]
        )
        self.assertState(
            'POST',
            CREATE_PATH % 1, # 1 is Silver (pay) account
            [
                clean_db,
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
        
        
        
        
    def test_change_payment_method(self):
        """
        """
        security.check(self, CHANGE_PM_PATH)
        
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
        
        # Todo: finish
        def account_has_no_payment_method(client, parameters):
            return client, parameters
        
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
                )
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
        
        def gateway_cancel_called(client, response, testcase):
            assert recurring_payment.gateway.cancel_payment_called
            
        # This state relies on the existance of the payment
        # created in the state test above..
        # TODO: make it separate
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
                )
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
        
        
        
