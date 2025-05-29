from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


CustomUser = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField()
    password2 = forms.CharField()

    class Meta:
        model = CustomUser
        fields = ("first_name", "email")
        widgets = {
            "first_name": forms.TextInput(),
            "email": forms.EmailInput(),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("The user with this email already exists")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error(
                "password2",
                ValidationError("Passwords don't match", code="password_mismatch"),
            )

        return cleaned_data

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("first_name")
        if name == "":
            self.add_error(
                "first_name",
                ValidationError("This field is required.", code="empty_name"),
            )


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["avatar"]  # Оставляем только поле аватара
        widgets = {
            "avatar": forms.FileInput(attrs={"accept": ".jpg,.png"}),
        }
