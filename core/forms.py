from django import forms 
from phonenumber_field.formfields import PhoneNumberField


class SmsForm(forms.Form):
    
    phone = forms.CharField(max_length=15)
    message = forms.CharField(max_length=120, widget=forms.Textarea(), required=True)
