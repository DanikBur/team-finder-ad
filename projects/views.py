"""Вьюхи приложения projects."""
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .constants import PROJECTS_PAGE_SIZE
from .forms import ProjectForm
from .models import Project


def _with_relations(qs):
    """select_related/prefetch — чтобы не было N+1 в карточках."""
    return qs.select_related("owner").prefetch_related("participants")


def _page(request, qs):
    return Paginator(qs, PROJECTS_PAGE_SIZE).get_page(
        request.GET.get("page"),
    )


def _ajax_get_project(pk):
    """Возвращает проект по pk или JsonResponse 404 для AJAX-эндпоинтов."""
    project = Project.objects.filter(pk=pk).first()
    if project is None:
        return None, JsonResponse(
            {"status": "not_found"}, status=HTTPStatus.NOT_FOUND,
        )
    return project, None


def project_list(request):
    qs = _with_relations(Project.objects.all()).order_by("-created_at")
    page = _page(request, qs)
    return render(
        request,
        "projects/project_list.html",
        {"projects": page.object_list, "page_obj": page},
    )


@login_required
def favorite_projects(request):
    qs = _with_relations(request.user.favorites.all()).order_by(
        "-created_at",
    )
    page = _page(request, qs)
    return render(
        request,
        "projects/favorite_projects.html",
        {"projects": page.object_list, "page_obj": page},
    )


def project_detail(request, pk):
    project = get_object_or_404(
        _with_relations(Project.objects.all()), pk=pk,
    )
    return render(
        request,
        "projects/project-details.html",
        {"project": project},
    )


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.owner = request.user
        obj.save()
        obj.participants.add(request.user)
        return redirect("projects:detail", obj.pk)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False},
    )


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id and not request.user.is_staff:
        return redirect("projects:detail", project.pk)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects:detail", project.pk)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True},
    )


@login_required
@require_POST
def complete_project(request, pk):
    project, missing = _ajax_get_project(pk)
    if missing is not None:
        return missing
    if project.owner_id != request.user.id:
        return JsonResponse(
            {"status": "forbidden"}, status=HTTPStatus.FORBIDDEN,
        )
    if project.status != Project.OPEN:
        return JsonResponse(
            {"status": "error", "project_status": project.status},
            status=HTTPStatus.BAD_REQUEST,
        )
    project.status = Project.CLOSED
    project.save(update_fields=["status"])
    return JsonResponse(
        {"status": "ok", "project_status": Project.CLOSED},
    )


@login_required
@require_POST
def toggle_participate(request, pk):
    project, missing = _ajax_get_project(pk)
    if missing is not None:
        return missing
    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        return JsonResponse({"status": "ok", "participant": False})
    project.participants.add(request.user)
    return JsonResponse({"status": "ok", "participant": True})


@login_required
@require_POST
def toggle_favorite(request, pk):
    project, missing = _ajax_get_project(pk)
    if missing is not None:
        return missing
    if request.user.favorites.filter(pk=project.pk).exists():
        request.user.favorites.remove(project)
        return JsonResponse({"status": "ok", "favorited": False})
    request.user.favorites.add(project)
    return JsonResponse({"status": "ok", "favorited": True})
