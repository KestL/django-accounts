from django.test import Client, TestCase
from django.contrib.auth.models import User
from account.models import Account
from account import subscription
from django.conf import settings

class AccountTests(TestCase):
    def setUp(self):
        """
        Define subscription levels. This overrides
        the levels defined in your settings.py file. 
        """
        self.gold = {
               'name': 'Gold Membership',
               'description': 'The gold membership is for...',
               'first_month_price': 20000,
               'recurring_price': 20000,
               'period': 30,
               'trial': 30,
               'resources': {
                   'people': 10,
                   'disk': 10000,
                   'chat': True,
                   'ssl': True,
                   'projects': subscription.Unlimited,
               }
        }
        self.silver = {
               'name': 'Silver Membership',
               'description': 'The silver membership is for...',
               'first_month_price': 10000,
               'recurring_price': 10000,
               'period': 30,
               'trial': 30,
               'resources': {
                   'people': 3,
                   'disk': 1000,
                   'chat': True,
                   'ssl': False,
                   'projects': 3,
               }
        }
        settings.SUBSCRIPTION_LEVELS = (
            self.gold, 
            self.silver,
        )
        settings.SUBSCRIPTION_REGULATORS = {
            'people': subscription.count('account', 'Person'),
            'disk': subscription.class_method('account', 'Account', 'disk_used'),
            'projects': subscription.class_method('account', 'Account', 'projects_count')
        }   
        Account.disk_used = lambda a: 1000
        Account.projects_count = lambda a: 65535
        
        
    def make_account(self, level=1, people=1):
        """
        Utility method: creates an account with
        a specific subscription level and # people
        """
        account = Account(
            subscription_level_id = level,
        )
        account.save()
        for i in range(people):
            account.person_set.create(
                username = 'person %i' % i,
                password = 'password %i' % i,
                first_name = 'first_name %i' % i,
                last_name = 'last_name %i' % i,
                email = 'email_%i@email.com' % i,
            )
        return account
        
    
    def test_silver_subscription_level(self):
        """
        Tests one of the subscription levels defined
        in setUp()
        """
        account = self.make_account(level = 1, people = 2)
        assert account.subscription_level == self.silver
        assert not account.has_resource('ssl')
        assert not account.has_resource('disk')
        assert not account.has_resource('projects')
        assert account.has_resource('people')
        
        
    def test_gold_subscription_level(self):
        """
        Tests one of the subscription levels defined
        in setUp()
        """
        account = self.make_account(level = 0, people = 10)
        assert account.subscription_level == self.gold
        assert account.has_resource('ssl')
        assert account.has_resource('disk')
        assert account.has_resource('projects')
        assert not account.has_resource('people')
        