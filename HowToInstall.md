# Introduction #

The account application is set up as described in: http://code.djangoproject.com/wiki/BestPracticesToWorkWith3rdPartyAppsAndMakingYoursPortable

The following steps assume you put the 'account' module in the directory 'c:\web\shared\'. If you use another directory, just substitute.

**Steps:**
  1. Do the checkout
```
svn checkout http://django-accounts.googlecode.com/svn/trunk/
```
  1. Disable the default session middleware in your project's setup.py
```
#'django.contrib.sessions.middleware.SessionMiddleware',
```
  1. Add the following to your project's setup.py
```
DEVELOPMENT = True 
if DEVELOPMENT: 
    import sys 
    sys.path.append('C:/web/shared') # Use your actual directory
)
PERSISTENT_SESSION_KEY = 'sessionpersistent'
SESSION_COOKIE_AGE = 120960

MIDDLEWARE_CLASSES = (
    ... < other middleware >...
    'account.middleware.DualSessionMiddleware',
    'account.middleware.AccountBasedAuthentication',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    ... < other processors >...
    "account.middleware.add_account_to_context",
)    
INSTALLED_APPS = (
    ... < other apps >...
    'account',
)
TEMPLATE_DIRS = (
    ... < other dirs >...
    "C:/web/shared/account/templates", # Use your actual directory
)

```
  1. If you use modpython, add c:/web/shared (or your actual path) to the pythonpath in apache your apache configuration file.
  1. Add the following line to your project's urls.py file
```
(r'^person/', include('account.person_urls')),
```

