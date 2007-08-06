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
    
    
class SignupForm(forms.Form):
    first_name = forms.CharField(
        label = "First name",
        min_length = 2,
        max_length = 30,        
    )
    last_name = forms.CharField(
        label = "Last name",
        min_length = 2,
        max_length = 30,        
    )
    email = forms.EmailField(
        label = "Email",
    )
    username = forms.CharField(
        label = "Username",
        help_text = "You'll use this to log in",
        min_length = 4,
        max_length = 30,        
    )
    password = forms.CharField(
        label = "Password",
        min_length = 6,
        max_length = 20,
        widget = forms.PasswordInput()
    )
    password2 = forms.CharField(
        label = "Password again",
        help_text = "Confirm your password by entering it again",
        min_length = 6,
        max_length = 20,
        widget = forms.PasswordInput()
    )
    group = forms.CharField(
        label = "Company / Organization",
        min_length = 2,
        max_length = 30,        
    )
    timezone = forms.ChoiceField(
        label = "Time zone",
        choices = enumerate(['central', 'eastern', 'etc'])
    )
    subdomain = forms.CharField(
        min_length = 2,
        max_length = 30,        
    )
    domain = forms.ChoiceField(
        choices = enumerate(settings.ACCOUNT_DOMAINS)
    )
            
    card_type = forms.ChoiceField(
        label = "Card type",
        choices = enumerate(['Visa', 'Mastercard', 'American Express'])
    )
    
    card_number = forms.CharField(
        label = "Card number",
        min_length = 10,
        max_length = 20,        
    )
    card_expiration = forms.DateField(
        label = "Expiration",
    )

    terms_of_service = forms.BooleanField(
        label = "I agree to the Terms of Service, Refund, and Privacy policies"
    )
        
        
    
    


