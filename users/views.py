"""Вьюхи приложения users."""
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .constants import USERS_PAGE_SIZE
from .forms import PasswordForm, ProfileForm, SignInForm, SignUpForm
from .models import User


def _filtered_users(queryset, filter_key, me):
    """Применяет к queryset фильтр по выбранному критерию.

    Возвращает исходный queryset, если ключ не распознан.
    """
    match filter_key:
        case "owners-of-favorite-projects":
            return queryset.filter(
                owned_projects__in=me.favorites.all(),
            ).distinct()
        case "owners-of-participating-projects":
            return queryset.filter(
                owned_projects__in=me.participated_projects.all(),
            ).distinct()
        case "interested-in-my-projects":
            return queryset.filter(
                favorites__in=me.owned_projects.all(),
            ).distinct()
        case "participants-of-my-projects":
            return (
                queryset.filter(
                    participated_projects__in=me.owned_projects.all(),
                )
                .exclude(pk=me.pk)
                .distinct()
            )
        case _:
            return queryset


def signup(request):
    if request.user.is_authenticated:
        return redirect("projects:list")
    form = SignUpForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("users:login")
    return render(request, "users/register.html", {"form": form})


def signin(request):
    if request.user.is_authenticated:
        return redirect("projects:list")
    form = SignInForm(request.POST or None, request=request)
    if form.is_valid():
        login(request, form.user)
        return redirect("projects:list")
    return render(request, "users/login.html", {"form": form})


def signout(request):
    logout(request)
    return redirect("projects:list")


def participants(request):
    queryset = User.objects.all()
    chosen = request.GET.get("filter") or ""
    if chosen and request.user.is_authenticated:
        queryset = _filtered_users(queryset, chosen, request.user)
    page = Paginator(queryset, USERS_PAGE_SIZE).get_page(
        request.GET.get("page"),
    )
    return render(
        request,
        "users/participants.html",
        {
            "participants": page.object_list,
            "page_obj": page,
            "active_filter": chosen,
        },
    )


def profile(request, pk):
    return render(
        request,
        "users/user-details.html",
        {"user": get_object_or_404(User, pk=pk)},
    )


@login_required
def profile_edit(request):
    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )
    if form.is_valid():
        form.save()
        return redirect("users:detail", request.user.id)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def password_change(request):
    form = PasswordForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("users:detail", request.user.id)
    return render(request, "users/change_password.html", {"form": form})
