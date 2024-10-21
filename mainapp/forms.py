from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Add City'))
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Add Category'))

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'quantity', 'discount', 'category', 'description', 'image','gender']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Add Product'))
class CustomUserCreationForm(UserCreationForm):
    phone_regex = RegexValidator(
        regex=r'^(?:056|059)\d{7}$',
        message="Phone number must be entered in the format: '056xxxxxxx' or '059xxxxxxxx'."
    )

    phone_number = forms.CharField(
        validators=[phone_regex],

        max_length=15,
        help_text="Enter phone number"
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'phone_number','whatsapp', 'password1', 'password2')


class CustomAuthenticationForm(AuthenticationForm):
    phone_regex = RegexValidator(
        regex=r'^(?:056|059)\d{7}$',
        message="Phone number must be entered in the format: '056xxxxxxx' or '059xxxxxxxx'."
    )
    username = forms.CharField(
        label="Phone Number",
        max_length=15,
        validators=[phone_regex],
        help_text="Enter phone number "
    )

    def clean(self):
        phone_number = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if phone_number is not None and password:
            self.user_cache = authenticate(phone_number=phone_number, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Invalid phone number or password.")
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class CustomUserUpdateForm(forms.ModelForm):
    phone_regex = RegexValidator(
        regex=r'^(?:056|059)\d{7}$',
        message="Phone number must be entered in the format: '056xxxxxxx' or '059xxxxxxxx'."
    )

    phone_number = forms.CharField(
        validators=[phone_regex],
        max_length=15,
        help_text="Enter phone number"
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number','whatsapp']

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(phone_number=phone_number).exists():
            raise forms.ValidationError("A user with this phone number already exists.")

        return phone_number
