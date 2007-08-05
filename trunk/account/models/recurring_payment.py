from datetime import date, timedelta, datetime
from django.db import models
from django.conf import settings
from account.lib import payment
from accounts import Account

gateway = getattr(payment, settings.PAYMENT_GATEWAY)

class RecurringPayment(models.Model):
    class Admin:
        pass
    
    class Meta:
        app_label = 'account'
        
    name = models.CharField(
        maxlength = 100,
    )
    number = models.CharField(
        maxlength = 20,
    )
    amount = models.CharField(
        maxlength = 10,
    )
    
    period = models.IntegerField(
    )
    
    token = models.CharField(
        maxlength = 64,
    )
    
    gateway_token = models.CharField(
        maxlength = 64,
    )
    
    account = models.ForeignKey(
        to = Account, 
        unique = True
    )
    
    cancelled_at = models.DateTimeField(
        blank = True,
        null = True,
    )
    
    created_on = models.DateField(
        auto_now_add = True,
    )
    
    @classmethod
    def create(cls, account, amount, card_number, card_expires, first_name, last_name, period=1, **kwargs):
        
        token = str(account.id)
        
        gateway_token = gateway.start_payment(
            url = settings.PAYMENT_GATEWAY_URL,
            login = settings.PAYMENT_GATEWAY_LOGIN,
            password = settings.PAYMENT_GATEWAY_PASSWORD,
            token = token,
            amount = amount,
            card_number = card_number,
            card_expires = card_expires,
            first_name = first_name,
            last_name = last_name,
            period = period, 
            **kwargs
        )
        
        obj = cls(
            account = account,
            number = '*' * (len(card_number)-4) + card_number[-4:],
            name = ' '.join([first_name, last_name]),
            amount = '$' + amount,
            period = period,
            gateway_token = gateway_token,
            token = token
        )
        obj.save()
        return obj
        
    def change_amount(self, amount, **kwargs):
        gateway.change_payment(
            url = settings.PAYMENT_GATEWAY_URL,
            login = settings.PAYMENT_GATEWAY_LOGIN,
            password = settings.PAYMENT_GATEWAY_PASSWORD,            
            amount = amount,
            gateway_token = self.gateway_token,
            **kwargs
        )
        self.amount = '$' + amount
        self.save()
        
    def cancel(self, **kwargs):
        gateway.cancel_payment(
            url = settings.PAYMENT_GATEWAY_URL,
            login = settings.PAYMENT_GATEWAY_LOGIN,
            password = settings.PAYMENT_GATEWAY_PASSWORD,            
            gateway_token = self.gateway_token,
            **kwargs
        )
        self.cancelled_at = datetime.now()
        self.save()
        
    
    def is_active(self):
        return not self.cancelled_at
        
    def is_expired(self, when=None):
        if not self.cancelled_at:
            return False
        
        from dateutil.rrule import rrule, MONTHLY
        last_day = rrule(
            MONTHLY, 
            dtstart = self.created_on,
            interval = self.period,
        ).after(self.cancelled_at)
        
        return last_day < (when or datetime.now())
            
        
    
    
    
    
    
    
    
    
    
    
    
    
    
