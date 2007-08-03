from django.conf.urls.defaults import *
from models.person import Person
from views import person_forms

def _auth(method):
    return 'account.views.authentication.' + method

urlpatterns = patterns('',
    (
        r'^login/$', 
        _auth('login'), 
        {
            'meta': {
                'requires_logout': True,
            },
        }
    ),
    (
        r'^logout/$', 
        _auth('logout'), 
        {
            'meta': {
                'requires_login': True,
            },
        }
    ),
    (
        r'^reset_password/$', 
        _auth('reset_password'), 
        {
            'meta': {
                'requires_logout': True,
            },
        }
    ),
    (
        r'^reset_password_success/$',  
        'django.views.generic.simple.direct_to_template', 
        {
            'template': 'reset_password_success.html'
        }
    ),
    (
        r'^change_password/(\d+)/$', 
        _auth('change_password'),
        {
            'meta': {
                'roles': 'account_admin',
            },
        }
    ),
    (
        r'^change_password/$', 
        _auth('change_own_password'),
        {
            'meta': {
                'requires_login': True,
            },
        }
    ),
    
    (
        r'^/$', 
        _auth('edit_self'),
        {
            'meta': {
                'requires_login': True,
            },
        }
    ),
    (
        r'^list/$', 
        'account.views.generic.list',
        {
            'meta': {
                'roles': 'account_admin',
            },
            'allow_empty': True,
            'queryset': Person.objects.all()
        }
    ),
    (
        r'^create/$', 
        'account.views.generic.create',
        {
            'meta': {
                'roles': 'account_admin',
            },
            'model': Person,
            'post_save_redirect': '/person/list/',
        }
    ),
    (
        r'^edit/(\d+)/$', 
        'account.views.generic.edit',
        {
            'meta': {
                'roles': 'account_admin',
            },
            'model': Person,
            'post_save_redirect': '/person/list/',
        }
    ),
    (
        r'^destroy/(\d+)/$', 
        'account.views.generic.destroy',
        {
            'meta': {
                'roles': 'account_admin',
            },
            'model': Person,
            'post_destroy_redirect': '/person/list/',
        }
    ),
)
