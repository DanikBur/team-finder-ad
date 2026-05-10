from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("list/", views.participants, name="list"),
    path("register/", views.signup, name="register"),
    path("login/", views.signin, name="login"),
    path("logout/", views.signout, name="logout"),
    path("edit-profile/", views.profile_edit, name="edit_profile"),
    path(
        "change-password/", views.password_change, name="change_password"
    ),
    path("<int:pk>/", views.profile, name="detail"),
]
