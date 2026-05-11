from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from .constants import (
    NAME_MAX_LENGTH,
    PROFILE_ABOUT_ROWS,
    SURNAME_MAX_LENGTH,
)
from .models import User
from .utils import to_e164


class SignUpForm(forms.ModelForm):
    name = forms.CharField(label="Имя", max_length=NAME_MAX_LENGTH)
    surname = forms.CharField(label="Фамилия", max_length=SURNAME_MAX_LENGTH)
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]

    def clean_email(self):
        value = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=value).exists():
            raise forms.ValidationError(
                "Пользователь с таким email уже существует"
            )
        return value

    def save(self, commit=True):
        return User.objects.create_user(
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            name=self.cleaned_data["name"],
            surname=self.cleaned_data["surname"],
        )


class SignInForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        data = super().clean()
        email, password = data.get("email"), data.get("password")
        if email and password:
            user = authenticate(
                self.request, username=email, password=password
            )
            if user is None:
                raise forms.ValidationError("Неверный имейл или пароль")
            self.user = user
        return data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "Ссылка на Github",
        }
        widgets = {
            "about": forms.Textarea(attrs={"rows": PROFILE_ABOUT_ROWS}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone") or ""
        if not phone:
            return phone
        phone = to_e164(phone)
        qs = User.objects.filter(phone=phone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                "Этот номер телефона уже используется"
            )
        return phone


class PasswordForm(PasswordChangeForm):
    pass
