from django.db import models
#from person import Person
from account import Account


class Role(models.Model):
    name = models.CharField(verbose_name = "Role name", maxlength = 40)
    #persons = models.ManyToManyField(to=Person, related_name='persons')
    
    class Admin:
        pass
    
    class Meta:
        app_label = 'account'
    

    def __unicode__(self):
        return self.name

        
