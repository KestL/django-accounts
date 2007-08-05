import unittest
import sys
from functional.account_tests import AccountTests
from functional.person_tests import PersonTests
from functional.recurring_payment_tests import RecurringPaymentTests
from integration.authentication_tests import AuthenticationTests
from integration.profile_tests import ProfileTests

test_cases = [
    AccountTests, 
    PersonTests, 
    RecurringPaymentTests, 
    AuthenticationTests,
    ProfileTests,
]

def suite():
    return unittest.TestSuite(
        [unittest.TestLoader().loadTestsFromTestCase(case) 
         for case in test_cases]
    )
    
