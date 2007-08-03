from django.http import HttpResponse, HttpResponseRedirect
from operator import eq
from urlparse import urlparse
from django.core import mail
from account.models import Person, Account

class Void: pass

def logged_in(client, response, testcase):
    """ Check that the default person is logged in """
    person = Person.objects.get(username = 'snhorne')
    
    # client.previous_request is only available
    # in patched test client.
    if hasattr(client, 'previous_request'):
        testcase.assertEqual(
            client.previous_request.person,
            person
        )
    testcase.assertEqual(
        client.session[Person.SESSION_KEY],
        person.id,
    )
        
def not_logged_in(client, response, testcase):
    """ Check that noone is logged in """
    # client.previous_request is only available
    # in patched test client.
    if hasattr(client, 'previous_request'):
        testcase.assertEqual(
            getattr(client.previous_request, 'person', None),
            None
        )
    
def status(code):
    """ Check the HTTP response status code """
    def has_status(client, response, testcase):
        testcase.assertEqual(
            response.status_code,
            code
        )
    return has_status
    
def rendered(template):
    """ Check that the template was rendered """
    def was_rendered(client, response, testcase):
        testcase.assertTemplateUsed(response, template)
    return was_rendered

def redirected(path):
    """ Check that user was redirected to path """
    def was_redirected(client, response, testcase):
        testcase.assertRedirects(response, path)
    return was_redirected
    
def context(key, value = Void, type = Void):
    """ Check that a key exists in context w/ matching value """
    def is_in_context(client, response, testcase):
        assert key in response.context
        if value is not Void:
            testcase.assertEqual(
                value, 
                response.context[key]
            )
        if type is not Void:
            testcase.assertTrue(
                isinstance(
                    response.context[key], 
                    type
                )
            )
            
    return is_in_context

def form_errors(name):
    def has_errors(client, response, testcase):
        assert name in response.context
        assert response.context[name]._errors
            
    return has_errors

    
    
    
def outbox_len(count):
    """ Check that the email.outbox contains n items """
    def outbox_len_is(client, response, testcase):
        testcase.assertEqual(
            len(mail.outbox),
            count
        )
    return outbox_len_is
        

def logged_in_has_password(password):
    """ Check that a password matches that of the logged in user """
    def check_password(client, response, testcase):
        # client.previous_request is only available
        # in patched test client.
        if hasattr(client, 'previous_request'):
            assert client.previous_request.person.check_password(password)
    return check_password
    
def person_has_password(pk, password):
    def check_password(client, response, testcase):
        assert Person.objects.get(pk = pk).check_password(password)
    return check_password
        

def session_expires_on_close(client, response, testcase):
    testcase.assertEqual(
        response.cookies['sessionid']['max-age'],
        ''
    )
    
def session_persists_after_close(client, response, testcase):
    testcase.assertTrue(
        int(response.cookies['sessionid']['max-age'] or '0') > 0
    )
    
def created(ModelClass):
    def check_created(client, response, testcase):
        old_count = client.alters[ModelClass]
        testcase.assertEqual(
            ModelClass.objects.count(),
            old_count + 1
        )
    return check_created
    
def does_not_exist(ModelClass, pk):
    def check_exist(client, response, testcase):
        try:
            ModelClass.objects.get(pk=pk)
            raise False
        except ModelClass.DoesNotExist:
            pass
    return check_exist
    
def exists(ModelClass, pk):
    def check_exist(client, response, testcase):
        try:
            ModelClass.objects.get(pk=pk)
        except ModelClass.DoesNotExist:
            raise False
    return check_exist











