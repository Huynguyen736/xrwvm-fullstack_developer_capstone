"""Explicit API routes and React entry points, including direct deep links."""
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView

spa = TemplateView.as_view(template_name="index.html")
urlpatterns = [
    path("admin/", admin.site.urls),
    path("djangoapp/", include("djangoapp.urls")),
    path("about/", TemplateView.as_view(template_name="About.html")),
    path("contact/", TemplateView.as_view(template_name="Contact.html")),
    path("", spa),
    re_path(r"^(?:login|register|dealers)/?$", spa),
    re_path(r"^(?:dealer|postreview)/[0-9]+/?$", spa),
]
