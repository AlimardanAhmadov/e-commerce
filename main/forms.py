from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django import forms
from django_countries.fields import CountryField
from .models import Address, Profile, Seller


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
        return self.cleaned_data

    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user    


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'first_name',
            'last_name',
            'phone_number',
            'email',
        )


class AddressForm(forms.Form):
    address = forms.CharField(max_length=500, required=True)
    flat = forms.CharField(max_length=500, required=True)
    city = forms.CharField(max_length=250, required=True)
    region = forms.CharField(max_length=250, required=False)
    country = CountryField().formfield()
    postcode = forms.IntegerField(required=True)
    address_type = forms.CharField(max_length=20, required=True)


class BecomeSellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = (
            'first_name',
            'last_name',
            'phone_number',
            'company_name', 
            'info',
            'phone_number',
        )


class SellerLoginForm(forms.Form):
    username = forms.CharField(max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
        return self.cleaned_data

    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user   