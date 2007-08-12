from django.conf.urls.defaults import *

def _sub(method):
    return 'account.views.subscription.' + method

urlpatterns = patterns('',
    (
        r'^$', 
        _sub('edit_account'), 
        {
            'meta': {
                'requires_login': True,
                'roles': 'account_admin',
            },
        }
    ),
    (
        r'^upgrade/(\d+)/$', 
        _sub('upgrade'), 
        {
            'meta': {
                'requires_login': True,
                'roles': 'account_admin',
                'ssl': True,
            },
        }
    ),
    (
        r'^create/(\d+)/$', 
        _sub('create'), 
        {
            'meta': {
                'requires_account': False,
                'ssl': True,
            },
        }
    ),
    (
        r'^change_payment_method/$', 
        _sub('change_payment_method'), 
        {
            'meta': {
                'requires_login': True,
                'roles': 'account_admin',
                'ssl': True,
            },
        }
    ),
    (
        r'^cancel_payment_method/$', 
        _sub('cancel_payment_method'), 
        {
            'meta': {
                'requires_login': True,
                'roles': 'account_admin',
            },
        }
    ),
)
