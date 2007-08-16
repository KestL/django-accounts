from django.test import Client, TestCase
from django.template import Template, Context
from account.models import Account, Person
from account.tests.mocks import subscription_levels

class AccountTagsTests(TestCase):
        
    fixtures = [
        'test/accounts.json', 
        'test/people.json', 
        'test/groups.json', 
        'test/roles.json',
    ]
    
    def admin_context(self):
        return Context({
            'person': Person.objects.get(pk=2),
            'account': Account.objects.get(pk=1),
        })
    
    def person_context(self):
        return Context({
            'person': Person.objects.get(pk=1),
            'account': Account.objects.get(pk=1),
        })
        
    def test_role_tag(self):
        t = Template("")
        result = t.render(self.admin_context())
        import pdb; pdb.set_trace()
    
