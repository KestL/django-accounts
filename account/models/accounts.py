from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from account import subscription

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
    
    #TODO: Implement account-specific file storage
    #logo = PhotoField(
        #verbose_name = "Company Logo",
        #upload_to = 'logos/%y%m%d%H%M%S',
        #width = 100,
        #blank = True,
    #)
    
    created_on = models.DateTimeField(
        auto_now_add = True,
    )
    
    website = models.URLField(
        verify_exists = True,
        blank = True,
    )
    
    subscription_level_id = models.IntegerField(
        editable = False,
        default = 0,
    )   
    
    @property
    def subscription_level(self):
        return settings.SUBSCRIPTION_LEVELS[self.subscription_level_id]
    
        
    def has_resource(self, resource_name):
        resource = self.subscription_level['resources'][resource_name]
        if resource is subscription.Unlimited:
            return True
        return settings.SUBSCRIPTION_REGULATORS.get(resource_name, lambda a, v: v)(
            self,
            resource
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
        
        
