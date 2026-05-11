from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import (
    AdminPasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)
from django.utils.html import format_html

from .constants import ADMIN_AVATAR_THUMB_PX
from .models import User


class CreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "name", "surname")


class EditForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    add_form = CreateForm
    form = EditForm
    change_password_form = AdminPasswordChangeForm
    model = User

    list_display = (
        "id", "thumb", "email", "name", "surname", "is_staff", "is_active"
    )
    list_display_links = ("id", "email")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "name", "surname")
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined", "last_login")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Личное", {
            "fields": (
                "name", "surname", "avatar", "about", "phone", "github_url"
            ),
        }),
        ("Права", {
            "fields": (
                "is_active", "is_staff", "is_superuser",
                "groups", "user_permissions",
            ),
        }),
        ("Даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "name", "surname", "password1", "password2"
            ),
        }),
    )

    @admin.display(description="Аватар")
    def thumb(self, obj):
        if not obj.avatar:
            return ""
        return format_html(
            '<img src="{}" width="{}" height="{}" '
            'style="border-radius:50%;object-fit:cover" />',
            obj.avatar.url, ADMIN_AVATAR_THUMB_PX, ADMIN_AVATAR_THUMB_PX,
        )
