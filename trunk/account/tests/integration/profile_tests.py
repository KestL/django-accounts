import re
from django.test import TestCase, Client
from django.core import mail
from account.models import Person, Account
import django.newforms as forms
from base import IntegrationTest
import security
import causes
import effects

LIST_PATH = '/person/list/'
CREATE_PATH = '/person/create/'
EDIT_PATH = '/person/edit/1/'
EDIT_PATH_INVALID = '/person/edit/999/'
EDIT_PATH_MISMATCH = '/person/edit/3/'

DESTROY_PATH = '/person/destroy/1/'
DESTROY_PATH_INVALID = '/person/destroy/999/'
DESTROY_PATH_OWNER = '/person/destroy/2/'
DESTROY_PATH_MISMATCH = '/person/destroy/3/'
    
class ProfileTests(IntegrationTest):
    fixtures = ['test/accounts.json', 'test/people.json']
    
    def test_list(self):
        """
        Tests for profile.list
        """
        def people_match_account(client, response, testcase):
            # client.previous_request is only available
            # in patched test client.
            if hasattr(client, 'previous_request'):
                people = response.context['object_list']           
                expected = Person.objects.filter(account = client.previous_request.account)
                assert len(people) == len(expected)
                for p in people:
                    assert p in expected
            
            
        security.check(self, LIST_PATH)
        self.assertState(
            'GET/POST',
            LIST_PATH,
            [
                causes.owner_logged_in,
                causes.valid_domain,
            ],
            [
                people_match_account,
                effects.rendered('account/person_list.html'),
                effects.status(200),
            ]
        )
    
    def test_create(self):
        """
        Tests for profile.create
        """
        security.check(self, CREATE_PATH, causes.ssl)
        
        self.assertState(
            'GET',
            CREATE_PATH,
            [
                causes.ssl,
                causes.owner_logged_in,
                causes.valid_domain,
            ],
            [
                effects.rendered('account/person_form.html'),
                effects.context('form', type = forms.BaseForm),
                effects.status(200),
            ]
        )
        self.assertState(
            'POST',
            CREATE_PATH,
            [
                causes.ssl,
                causes.owner_logged_in,
                causes.valid_domain,
                causes.invalid_create_person_parameters,
            ],
            [
                effects.rendered('account/person_form.html'),
                effects.context('form', type = forms.BaseForm),
                effects.form_errors('form'),
                effects.status(200),
            ]
        )
        self.assertState(
            'POST',
            CREATE_PATH,
            [
                causes.ssl,
                causes.alters(Person),
                causes.owner_logged_in,
                causes.valid_domain,
                causes.valid_create_person_parameters,
            ],
            [
                effects.created(Person),
                effects.redirected('/person/list/'),
            ]
        )
    
    
    def test_edit(self):
        """
        Tests for profile.edit
        """
        security.check(self, EDIT_PATH)
        self.assertState(
            'GET',
            EDIT_PATH,
            [
                causes.owner_logged_in,
                causes.valid_domain,
            ],
            [
                effects.rendered('account/person_form.html'),
                effects.context('form', type = forms.BaseForm),
                effects.status(200),
            ]
        )
        self.assertState(
            'GET/POST',
            EDIT_PATH_INVALID,
            [
                causes.owner_logged_in,
                causes.valid_domain,
            ],
            [
                effects.status(404),
            ]
        )
        self.assertState(
            'GET/POST',
            EDIT_PATH_MISMATCH,
            [
                causes.owner_logged_in,
                causes.valid_domain,
            ],
            [
                effects.status(404),
            ]
        )
        self.assertState(
            'POST',
            EDIT_PATH,
            [
                causes.owner_logged_in,
                causes.valid_domain,
                causes.invalid_create_person_parameters,
            ],
            [
                effects.rendered('account/person_form.html'),
                effects.context('form', type = forms.BaseForm),
                effects.form_errors('form'),
                effects.status(200),
            ]
        )
        
        def change_person(client, parameters):            parameters.update({
                'username': 'bob_jones',
                'password': 'password',
                'first_name': 'bob',
                'last_name': 'jones',
                'email': 'bob@email.com',
            })
            return client, parameters
            
        def person_was_changed(client, response, testcase):
            person = Person.objects.get(pk = 1)
            assert person.first_name == 'bob'
    
        self.assertState(
            'POST',
            EDIT_PATH,
            [
                causes.alters(Person),
                causes.owner_logged_in,
                causes.valid_domain,
                change_person
            ],
            [
                person_was_changed,
                effects.redirected('/person/list/'),
            ]
        )
    
    
    def test_destroy(self):
        """
        Tests for profile.destroy
        """
        security.check(self, DESTROY_PATH)
        self.assertState(
            'GET',
            DESTROY_PATH,
            [
                causes.owner_logged_in,
                causes.valid_domain,
            ],
            [
                effects.status(405),
            ]
        )
    
        self.assertState(
            'POST',
            DESTROY_PATH_INVALID,
            [
                causes.owner_logged_in,
                causes.valid_domain,
            ],
            [
                effects.status(404),
            ]
        )
        
        self.assertState(
            'POST',
            DESTROY_PATH_MISMATCH,
            [
                causes.owner_logged_in,
                causes.valid_domain,
            ],
            [
                effects.status(404),
            ]
        )
        
        
        self.assertState(
            'POST',
            DESTROY_PATH,
            [
                causes.owner_logged_in,
                causes.valid_domain,
            ],
            [
                effects.does_not_exist(Person, id = 1),
                effects.redirected('/person/list/')
            ]
        )
    
        self.assertState(
            'POST',
            DESTROY_PATH_OWNER,
            [
                causes.owner_logged_in,
                causes.valid_domain,
            ],
            [
                effects.exists(Person, id = 2),
                effects.status(403)
                
            ]
        )
    
    
    
    
    
    
    
    
    
    
    