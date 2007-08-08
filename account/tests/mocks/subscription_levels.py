from django.conf import settings

settings.SUBSCRIPTION_LEVELS = (
    {
        'name': 'Free Membership',
        'description': 'The free membership is for...',
        'price': 0,
        'resources': {
            'people': 10,
            'disk': 1000,
            'chat': True,
            'ssl': True,
        }
    },
    {
        'name': 'Silver Membership',
        'description': 'The silver membership is for...',
        'price': 10000,
        'period': 1,
        'trial': 1,
        'resources': {
            'people': 10,
            'disk': 1000,
            'chat': True,
            'ssl': True,
        }
    },
    {
        'name': 'Gold Membership',
        'description': 'The gold membership is for...',
        'price': 20000,
        'period': 1,
        'trial': 1,
        'resources': {
            'people': 10,
            'disk': 1000,
            'chat': True,
            'ssl': True,
        }
    },
    
    
)

