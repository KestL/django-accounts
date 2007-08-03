from django.db import models
from django.contrib.auth.models import User
from verdjnlib.fields import PhotoField

class Account(models.Model):
    
    class Admin:
        pass
    
    class Meta:
        app_label = 'account'
    
    domain = models.CharField(
        verbose_name = "Domain Name",
        maxlength = 40,
        unique = True,
    )
    
    name = models.CharField(
        verbose_name = "Account Name",
        maxlength = 40,
    )
    
    logo = PhotoField(
        verbose_name = "Company Logo",
        upload_to = 'logos/%y%m%d%H%M%S',
        width = 100,
        blank = True,
    )
    
    created_on = models.DateTimeField(
        auto_now_add = True,
    )
    
    website = models.URLField(
        verify_exists = True,
        blank = True,
    )
    
    def __unicode__(self):
        return self.name

    @classmethod
    def load_from_request(cls, request):
        try:
            request.account = Account.objects.get(
                domain = request.META['HTTP_HOST'],
            )        
        except (models.ObjectDoesNotExist, KeyError):
            request.account = None
            
        return request.account
        
