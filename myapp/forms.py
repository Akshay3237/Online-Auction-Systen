from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import User,AuctionItem
from .models import Image

class EditProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'contact_no')

class AuctionItemForm(forms.ModelForm):
    class Meta:
         model = AuctionItem
         fields = ['name', 'description', 'category', 'base_price', 'start_time', 'end_time']
         widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
         }


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']

class EditAuctionForm(forms.ModelForm):
    class Meta:
        model = AuctionItem
        fields = ['name', 'description', 'base_price', 'start_time', 'end_time']