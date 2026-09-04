from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("members/", views.member_list, name="member-list"),
    path("members/add/", views.member_add, name="member-add"),
    path("members/<int:pk>/edit/", views.member_edit, name="member-edit"),
    path("members/<int:pk>/delete/", views.member_delete, name="member-delete"),
]
