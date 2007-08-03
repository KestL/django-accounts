import new
from django.conf import settings
from django import newforms as forms
from ..models import Person

class LoginForm(forms.Form):
    
    username = forms.CharField(
        label = 'Username',
    )
    
    password = forms.CharField(
        label = 'Password', 
        widget = forms.PasswordInput,
    )        
    
    remember_me = forms.BooleanField(
        label = 'Remember me on this computer', 
        required = False,
    )        
    
    person = None
    account = None
    
    def clean(self):
        if self._errors: 
            return
        
        self.person = Person.authenticate(
            self.data['username'],
            self.account,
            self.data['password'],
        )
        
        if self.person is None:
            raise forms.ValidationError(
                "Your username and password didn't match. Did you spell them right?",
            )
        return self.cleaned_data
    
    def login(self, request):
        self.account = request.account
        if self.is_valid():
            request.session[
                 settings.PERSISTENT_SESSION_KEY
            ] = self.cleaned_data['remember_me']
                
            self.person.login(request)
            return True
        return False

    
# TODO: Need more elegant solution.    
class ResetPasswordForm(forms.Form):
    username = forms.CharField(
        label = 'Username',
    )
    
    person = None
    account = None
    
    def clean(self):
        if self._errors: 
            return
        try:
            self.person = Person.objects.get(
                username = self.data['username'],
                account = self.account,
            )
        except Person.DoesNotExist:
            raise forms.ValidationError(
                "Your user name wasn't on file. Did you spell it correctly?",
            )
        
    def get_person(self, request):
        self.account = request.account
        if self.is_valid():
            return self.person

        
class ChangePasswordForm(forms.Form):    
    password = forms.CharField(
        min_length = 6,
        max_length = 20,
        widget = forms.PasswordInput()
    )
    password2 = forms.CharField(
        min_length = 6,
        max_length = 20,
        widget = forms.PasswordInput()
    )
    
    def clean(self):
        if self.data['password'] != self.data['password2']:
            raise forms.ValidationError(
                "The two passwords didn't match. Please try again."
            )
        return self.cleaned_data
                
            
        
    
    


